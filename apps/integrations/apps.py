from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.integrations"

    def ready(self):
        from .providers.github.provider import GitHubProvider
        from .providers.registry import GitProviderRegistry

        GitProviderRegistry.register("github", GitHubProvider)
