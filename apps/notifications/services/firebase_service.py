import logging
import os
from functools import lru_cache

import firebase_admin
from django.conf import settings
from firebase_admin import credentials, messaging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_firebase_app():
    app_name = "vurn"

    try:
        return firebase_admin.get_app(app_name)
    except ValueError:
        pass

    credential_path = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_PATH", None)

    if not credential_path or not os.path.isfile(credential_path):
        raise RuntimeError("Firebase service account credentials are not configured.")

    credential = credentials.Certificate(credential_path)

    return firebase_admin.initialize_app(credential, name=app_name)


class FirebasePushService:
    @staticmethod
    def send_to_token(*, token, title, body, data=None):
        app = get_firebase_app()

        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={
                str(key): str(value)
                for key, value in (data or {}).items()
                if value is not None
            },
            token=token,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(title=title, body=body)
            ),
        )

        return messaging.send(message, app=app)
