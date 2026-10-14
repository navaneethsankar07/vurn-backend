from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum
from django.utils import timezone

from ..constants import AI_FEATURE_CREDIT_COSTS
from ..models import AIUsageHistory, OrganizationAIWallet


class AIUsageStatisticsService:
    @staticmethod
    def get_statistics(*, organization):
        now = timezone.localtime()
        today = now.date()
        month_start = today.replace(day=1)

        usage_queryset = AIUsageHistory.objects.filter(
            organization=organization, feature__in=AI_FEATURE_CREDIT_COSTS.keys()
        )

        credits_used_today = (
            usage_queryset.filter(created_at__date=today).aggregate(
                total=Sum("credits_consumed")
            )["total"]
            or 0
        )

        credits_used_this_month = (
            usage_queryset.filter(
                created_at__date__gte=month_start, created_at__date__lte=today
            ).aggregate(total=Sum("credits_consumed"))["total"]
            or 0
        )

        elapsed_days = today.day

        average_daily_usage = (
            Decimal(credits_used_this_month) / Decimal(elapsed_days)
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        wallet_balance = (
            OrganizationAIWallet.objects.filter(organization=organization)
            .values_list("balance", flat=True)
            .first()
        )

        return {
            "remaining_ai_credits": wallet_balance or 0,
            "credits_used_today": credits_used_today,
            "credits_used_this_month": credits_used_this_month,
            "average_daily_usage": average_daily_usage,
        }
