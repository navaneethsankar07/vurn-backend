import requests

from ...exceptions import GitProviderException


class GitHubClient:

    BASE_URL = "https://api.github.com"

    def __init__(self, *, access_token):
        self.access_token = access_token

    def _request(self, *, method, endpoint, params=None, return_headers=False):
        response = requests.request(
            method,
            f"{self.BASE_URL}{endpoint}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.access_token}",
                "X-GitHub-Api-Version": "2026-03-10",
            },
            params=params,
            timeout=15,
        )

        if not response.ok:
            raise GitProviderException("GitHub API request failed.")

        data = response.json()

        if return_headers:
            return data, response.headers

        return data

    def get_installation_repositories(self):
        return self._request(method="GET", endpoint="/installation/repositories")

    def get_repository(self, *, owner, repository):
        return self._request(method="GET", endpoint=f"/repos/{owner}/{repository}")

    def get_commits(self, *, owner, repository, branch=None, page=1, per_page=30):
        params = {"page": page, "per_page": per_page}

        if branch:
            params["sha"] = branch

        commits, headers = self._request(
            method="GET",
            endpoint=f"/repos/{owner}/{repository}/commits",
            params=params,
            return_headers=True,
        )

        pagination = self._parse_pagination_headers(headers)

        return {"commits": commits, "pagination": pagination}

    @staticmethod
    def _parse_pagination_headers(headers):
        link_header = headers.get("Link")

        pagination = {"next": None, "previous": None, "first": None, "last": None}

        if not link_header:
            return pagination

        for link in link_header.split(","):
            url_part, rel_part = link.split(";", 1)

            url = url_part.strip().strip("<>")
            rel = rel_part.strip()

            if 'rel="next"' in rel:
                pagination["next"] = url

            elif 'rel="prev"' in rel:
                pagination["previous"] = url

            elif 'rel="first"' in rel:
                pagination["first"] = url

            elif 'rel="last"' in rel:
                pagination["last"] = url

        return pagination

    def get_branches(self, *, owner, repository):
        return self._request(
            method="GET", endpoint=f"/repos/{owner}/{repository}/branches"
        )

    def get_pull_requests(
        self, *, owner, repository, state="open", page=1, per_page=30
    ):
        params = {"state": state, "page": page, "per_page": per_page}

        pull_requests, headers = self._request(
            method="GET",
            endpoint=f"/repos/{owner}/{repository}/pulls",
            params=params,
            return_headers=True,
        )

        pagination = self._parse_pagination_headers(headers)

        return {"pull_requests": pull_requests, "pagination": pagination}

    def get_issues(
        self,
        *,
        owner,
        repository,
        state="open",
        sort="created",
        direction="desc",
        page=1,
        per_page=30,
    ):
        issues = []
        github_page = 1
        required_count = page * per_page
        pagination = {"next": None, "previous": None, "first": None, "last": None}

        while len(issues) < required_count:
            params = {
                "state": state,
                "sort": sort,
                "direction": direction,
                "page": github_page,
                "per_page": 100,
            }

            results, headers = self._request(
                method="GET",
                endpoint=f"/repos/{owner}/{repository}/issues",
                params=params,
                return_headers=True,
            )

            issues.extend(issue for issue in results if "pull_request" not in issue)

            pagination = self._parse_pagination_headers(headers)

            if pagination["next"] is None:
                break

            github_page += 1

        start = (page - 1) * per_page
        page_issues = issues[start : start + per_page]

        has_next = len(issues) > start + per_page

        return {
            "issues": page_issues,
            "pagination": {
                "next_page": page + 1 if has_next else None,
                "previous_page": page - 1 if page > 1 else None,
            },
        }
