import uuid

import razorpay
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from razorpay.errors import SignatureVerificationError

from apps.ai.constants import AI_CREDIT_PLANS
from apps.ai.models import AICreditPurchase
from apps.ai.services.wallet_service import OrganizationAIWalletService
from ..exceptions import AICreditPurchaseError, InvalidPaymentError


class AICreditPurchaseService:
    @staticmethod
    def get_client():
        key_id = getattr(settings, "RAZORPAY_KEY_ID", None)
        key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", None)

        if not key_id or not key_secret:
            raise AICreditPurchaseError(
                "Razorpay is not configured. Check the API credentials."
            )

        return razorpay.Client(auth=(key_id.strip(), key_secret.strip()))

    @staticmethod
    def create_order(*, organization, user, plan_key):
        plan = AI_CREDIT_PLANS.get(plan_key)

        if plan is None:
            raise AICreditPurchaseError("Invalid AI credit plan.")

        amount = plan["price_inr"] * 100
        client = AICreditPurchaseService.get_client()

        order = client.order.create(
            {
                "amount": amount,
                "currency": "INR",
                "receipt": uuid.uuid4().hex,
                "notes": {
                    "organization_id": str(organization.id),
                    "plan_key": plan_key,
                },
            }
        )

        purchase = AICreditPurchase.objects.create(
            organization=organization,
            user=user,
            plan_key=plan_key,
            credits=plan["credits"],
            amount=amount,
            currency="INR",
            razorpay_order_id=order["id"],
        )

        return {
            "purchase_id": purchase.id,
            "plan_key": plan_key,
            "plan_name": plan["name"],
            "credits": plan["credits"],
            "amount": amount,
            "currency": "INR",
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": order["id"],
        }

    @staticmethod
    def verify_payment(
        *, organization, razorpay_order_id, razorpay_payment_id, razorpay_signature
    ):
        client = AICreditPurchaseService.get_client()

        try:
            with transaction.atomic():
                purchase = AICreditPurchase.objects.select_for_update().get(
                    organization=organization, razorpay_order_id=razorpay_order_id
                )

                if purchase.status == "paid":
                    if purchase.razorpay_payment_id == razorpay_payment_id:
                        return {"status": "paid", "already_processed": True}

                    raise InvalidPaymentError("This order has already been paid.")

                client.utility.verify_payment_signature(
                    {
                        "razorpay_order_id": purchase.razorpay_order_id,
                        "razorpay_payment_id": razorpay_payment_id,
                        "razorpay_signature": razorpay_signature,
                    }
                )

                payment = client.payment.fetch(razorpay_payment_id)

                if payment.get("order_id") != purchase.razorpay_order_id:
                    raise InvalidPaymentError("Payment does not belong to this order.")

                if payment.get("status") != "captured":
                    raise InvalidPaymentError("Payment has not been captured.")

                if payment.get("amount") != purchase.amount:
                    raise InvalidPaymentError(
                        "Payment amount does not match the order."
                    )

                if payment.get("currency") != purchase.currency:
                    raise InvalidPaymentError(
                        "Payment currency does not match the order."
                    )

                OrganizationAIWalletService.add_credits(
                    organization=organization, credits=purchase.credits
                )

                purchase.razorpay_payment_id = razorpay_payment_id
                purchase.status = "paid"
                purchase.credited_at = timezone.now()
                purchase.save(
                    update_fields=[
                        "razorpay_payment_id",
                        "status",
                        "credited_at",
                        "updated_at",
                    ]
                )

                return {
                    "status": "paid",
                    "credits_added": purchase.credits,
                    "already_processed": False,
                }

        except AICreditPurchase.DoesNotExist as exc:
            raise InvalidPaymentError("Purchase order was not found.") from exc
        except SignatureVerificationError as exc:
            raise InvalidPaymentError("Payment signature verification failed.") from exc
