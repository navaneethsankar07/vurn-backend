from ..providers.registry import GitProviderRegistry


class GitProviderService:

    @staticmethod
    def get_provider(*, provider, **kwargs):
        provider_class = GitProviderRegistry.get(provider)

        return provider_class(**kwargs)
