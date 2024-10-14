import logging

import jwt
import requests

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html: str) -> dict:
    """
    Send an email using the Plunk API.

    Args:
        to (str or list): The recipient's email address(es).
        subject (str): The subject of the email.
        html (str): The HTML content of the email.
    """
    logger.info(f'Sending email to {to} with subject: {subject}')  # noqa: G004

    url = 'https://api.useplunk.com/v1/send'
    headers = {'Authorization': f'Bearer {settings.PLUNK_API_KEY}', 'Content-Type': 'application/json'}

    payload = {
        'subject': subject,
        'body': html,
        'to': to,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        logger.info(f'Email sent successfully to {to}')  # noqa: G004
    except requests.RequestException:
        logger.exception('Failed to send email')


def generate_access_token(user):
    payload = {
        'user_id': user.id,
        'iat': timezone.now(),
        'exp': timezone.now() + settings.JWT_AUTH['JWT_EXPIRATION_DELTA'],
    }
    return jwt.encode(payload, settings.JWT_AUTH['JWT_SECRET_KEY'], algorithm=settings.JWT_AUTH['JWT_ALGORITHM'])


def generate_refresh_token(user):
    payload = {
        'user_id': user.id,
        'iat': timezone.now(),
        'exp': timezone.now() + settings.JWT_AUTH['JWT_REFRESH_EXPIRATION_DELTA'],
    }
    return jwt.encode(payload, settings.JWT_AUTH['JWT_SECRET_KEY'], algorithm=settings.JWT_AUTH['JWT_ALGORITHM'])
