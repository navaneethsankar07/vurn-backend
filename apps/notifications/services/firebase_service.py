import json
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

    credential_json = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_JSON", None)
    if credential_json:
        try:
            credential_dict = (
                json.loads(credential_json)
                if isinstance(credential_json, str)
                else credential_json
            )
            credential = credentials.Certificate(credential_dict)
            return firebase_admin.initialize_app(credential, name=app_name)
        except Exception as exc:
            logger.error("Failed to initialize Firebase from JSON environment: %s", exc)

    credential_path = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_PATH", None)

    if not credential_path or not os.path.isfile(credential_path):
        raise RuntimeError("Firebase service account credentials are not configured.")

    credential = credentials.Certificate(credential_path)

    return firebase_admin.initialize_app(credential, name=app_name)


class FirebasePushService:
    @staticmethod
    def send_to_token(*, token, title, body, data=None):
        app = get_firebase_app()

        message_data = {
            "title": title,
            "body": body,
            **{
                str(key): str(value)
                for key, value in (data or {}).items()
                if value is not None
            },
        }

        message = messaging.Message(data=message_data, token=token)

        return messaging.send(message, app=app)
