from django.db import models
from django.conf import settings

from apps.ai.constants import AI_FEATURE_CHOICES


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


class AIUsageHistory(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="ai_usage_history",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_usage_history",
    )
    feature = models.CharField(max_length=50, choices=AI_FEATURE_CHOICES)
    credits_consumed = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_usage_history"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["organization", "-created_at"], name="idx_ai_usage_org_created"
            ),
            models.Index(
                fields=["user", "-created_at"], name="idx_ai_usage_user_created"
            ),
            models.Index(
                fields=["organization", "feature"], name="idx_ai_usage_org_feature"
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(credits_consumed__gt=0),
                name="ck_ai_usage_credits_positive",
            )
        ]

    def __str__(self):
        return (
            f"{self.feature} - {self.credits_consumed} credits "
            f"({self.organization.slug})"
        )
