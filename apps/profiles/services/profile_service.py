from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import User


class ProfileService:

    @staticmethod
    def get_profile(user: User) -> dict:
        now = timezone.now()

        return {
            "user": user,
            "statistics": {
                "organizations_joined": 4,
                "projects": 17,
                "assigned_issues": 42,
                "completed_issues": 128,
                "comments": 356,
                "github_linked_projects": 9,
            },
            "recent_activity": [
                {
                    "type": "issue_created",
                    "title": "Created issue VRN-142",
                    "description": "Improve workspace invitation states",
                    "timestamp": now - timedelta(minutes=18),
                },
                {
                    "type": "comment_added",
                    "title": "Commented on VRN-118",
                    "description": "Consolidate organization access controls",
                    "timestamp": now - timedelta(hours=2),
                },
                {
                    "type": "issue_closed",
                    "title": "Closed issue SPR-24",
                    "description": "July platform reliability sprint",
                    "timestamp": now - timedelta(days=1),
                },
                {
                    "type": "invitation_accepted",
                    "title": "Accepted invitation",
                    "description": "Joined via invite from Marcus Webb",
                    "timestamp": now - timedelta(days=3),
                },
                {
                    "type": "organization_joined",
                    "title": "Joined organization",
                    "description": "Added to the Platform team",
                    "timestamp": now - timedelta(days=7),
                },
                {
                    "type": "issue_created",
                    "title": "Created issue ACM-09",
                    "description": "Draft AI credit usage reporting spec",
                    "timestamp": now - timedelta(days=10),
                },
            ],
        }
