from apps.ai.constants import FREE_ORGANIZATION_AI_CREDITS
from apps.ai.models import OrganizationAIWallet


class OrganizationAIWalletService:

    @staticmethod
    def create_wallet(*, organization):
        wallet, created = OrganizationAIWallet.objects.get_or_create(
            organization=organization,
            defaults={
                "balance": FREE_ORGANIZATION_AI_CREDITS,
                "total_credited": FREE_ORGANIZATION_AI_CREDITS,
            },
        )
        return wallet
