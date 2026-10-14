from django.db import transaction

from ..constants import AI_FEATURE_CREDIT_COSTS, FREE_ORGANIZATION_AI_CREDITS
from ..models import OrganizationAIWallet
from ..exceptions import (
    InsufficientAICreditsError,
    UnsupportedAIFeatureError,
)
from .ai_usage_history_service import AIUsageHistoryService


class OrganizationAIWalletService:

    @staticmethod
    def create_wallet(*, organization):
        wallet, _ = OrganizationAIWallet.objects.get_or_create(
            organization=organization,
            defaults={
                "balance": FREE_ORGANIZATION_AI_CREDITS,
                "total_credited": FREE_ORGANIZATION_AI_CREDITS,
            },
        )
        return wallet

    @staticmethod
    def consume_credits(*, organization, user, feature):
        if feature not in AI_FEATURE_CREDIT_COSTS:
            raise UnsupportedAIFeatureError(f"Unsupported AI feature: {feature}")

        credits = AI_FEATURE_CREDIT_COSTS[feature]

        with transaction.atomic():
            wallet = OrganizationAIWallet.objects.select_for_update().get(
                organization=organization
            )

            if wallet.balance < credits:
                raise InsufficientAICreditsError(
                    "Your organization does not have enough AI credits."
                )

            wallet.balance -= credits
            wallet.total_consumed += credits
            wallet.save(update_fields=["balance", "total_consumed", "updated_at"])

            AIUsageHistoryService.objects.create(
                organization=organization,
                user=user,
                feature=feature,
                credits_consumed=credits,
            )

            return wallet
