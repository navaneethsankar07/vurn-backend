from ..constants import GIT_PROVIDER_CHOICES
from ..exceptions import GitProviderNotSupportedException


class GitProviderRegistry:
    _providers = {}

    @classmethod
    def register(cls, provider_name, provider_class):
        cls._providers[provider_name] = provider_class

    @classmethod
    def get(cls, provider_name):
        provider_class = cls._providers.get(provider_name)

        if provider_class is None:
            raise GitProviderNotSupportedException(
                f"Git provider '{provider_name}' is not supported."
            )

        return provider_class

    @classmethod
    def supported_providers(cls):
        return tuple(cls._providers.keys())
