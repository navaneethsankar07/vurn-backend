from apps.ai.constants import AI_FEATURE_CHOICES, AI_FEATURE_CREDIT_COSTS
from apps.ai.exceptions import InvalidAICreditCostError, UnsupportedAIFeatureError
from apps.ai.models import AIUsageHistory


class AIUsageHistoryService:

    @staticmethod
    def create_record(*, organization, user, feature, credits_consumed=None):
        valid_features = dict(AI_FEATURE_CHOICES)
        if feature not in valid_features:
            raise UnsupportedAIFeatureError(f"Unsupported AI feature: {feature}")

        expected_cost = AI_FEATURE_CREDIT_COSTS.get(feature)

        if expected_cost is not None:
            if credits_consumed is None:
                credits_consumed = expected_cost

            if credits_consumed != expected_cost:
                raise InvalidAICreditCostError(
                    f"Invalid credit cost for {feature}. "
                    f"Expected {expected_cost}, received {credits_consumed}."
                )

        return AIUsageHistory.objects.create(
            organization=organization,
            user=user,
            feature=feature,
            credits_consumed=credits_consumed or 0,
        )

    @staticmethod
    def get_usage_history(*, organization):
        return (
            AIUsageHistory.objects.filter(
                organization=organization, feature__in=dict(AI_FEATURE_CHOICES).keys()
            )
            .select_related("user")
            .order_by("-created_at")
        )
