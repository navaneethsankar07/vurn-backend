GIT_PROVIDER_CHOICES = (
    ("github", "GitHub"),
    ("gitlab", "GitLab"),
    ("bitbucket", "Bitbucket"),
)

GIT_INTEGRATION_STATUS_CHOICES = (
    ("active", "Active"),
    ("disconnected", "Disconnected"),
    ("error", "Error"),
)

GIT_REPOSITORY_VISIBILITY_CHOICES = (
    ("public", "Public"),
    ("private", "Private"),
)

GIT_PULL_REQUEST_STATE_CHOICES = (
    ("open", "Open"),
    ("closed", "Closed"),
    ("merged", "Merged"),
)

GIT_WEBHOOK_STATUS_CHOICES = (
    ("received", "Received"),
    ("processing", "Processing"),
    ("processed", "Processed"),
    ("failed", "Failed"),
)


STATE_SALT = "github-app-installation"
STATE_MAX_AGE = 600
