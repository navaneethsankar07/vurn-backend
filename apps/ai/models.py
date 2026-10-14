from django.db import models


class OrganizationAIWallet(models.Model):
    organization = models.OneToOneField(
        "organizations.Organization", on_delete=models.CASCADE, related_name="ai_wallet"
    )
    balance = models.PositiveIntegerField(default=0)
    total_credited = models.PositiveIntegerField(default=0)
    total_consumed = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organization_ai_wallets"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0),
                name="ck_org_ai_wallet_balance_nonnegative",
            )
        ]

    def __str__(self):
        return f"{self.organization.slug} - {self.balance} AI credits"
