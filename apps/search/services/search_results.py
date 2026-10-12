class ElasticsearchSearchResults:
    def __init__(self, query, allowed_project_ids, search_service):
        self.query = query
        self.allowed_project_ids = allowed_project_ids
        self.search_service = search_service

    def count(self):
        result = self.search_service.search(
            query=self.query,
            allowed_project_ids=self.allowed_project_ids,
            page=1,
            page_size=1,
        )
        return result["total"]

    def __len__(self):
        return self.count()

    def __getitem__(self, index):
        if isinstance(index, slice):
            start = index.start or 0
            stop = index.stop

            if stop is None:
                raise IndexError("An explicit slice end is required.")

            if start < 0 or stop < 0:
                raise IndexError("Negative indexing is not supported.")

            if stop <= start:
                return []

            result = self.search_service.search(
                query=self.query,
                allowed_project_ids=self.allowed_project_ids,
                page=(start // (stop - start)) + 1,
                page_size=stop - start,
            )

            return result["results"]

        if index < 0:
            raise IndexError("Negative indexing is not supported.")

        result = self.search_service.search(
            query=self.query,
            allowed_project_ids=self.allowed_project_ids,
            page=index + 1,
            page_size=1,
        )

        if not result["results"]:
            raise IndexError("Search result index out of range.")

        return result["results"][0]
