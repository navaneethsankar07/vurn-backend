from ..models import AICreditPurchase


class AICreditPurchaseHistoryService:
    @staticmethod
    def get_history(*, organization):
        return (
            AICreditPurchase.objects.filter(organization=organization)
            .select_related("user")
            .order_by("-created_at")
        )
