import logging

import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)

def _eskiz_token():
    token = cache.get("eskiz_token")
    if token:
        return token

    response = requests.post(
        "https://notify.eskiz.uz/api/auth/login",
        data={"email": settings.ESKIZ_EMAIL, "password": settings.ESKIZ_PASSWORD},
        timeout=10,
    )
    token = response.json()["data"]["token"]
    cache.set("eskiz_token", token, 60 * 60 * 24 * 20)   # ~20 kun
    return token


def _eskiz(phone, code):
    response = requests.post(
        "https://notify.eskiz.uz/api/message/sms/send",
        headers={"Authorization": f"Bearer {_eskiz_token()}"},
        data={
            "mobile_phone": phone,
            "message": f"Tasdiqlash kodingiz: {code}",
            "from": "4546",
        },
        timeout=10,
    )

    if response.status_code == 401:
        cache.delete("eskiz_token")       # token eskirgan — keyingi safar yangilanadi
        logger.error("Eskiz: token eskirgan")
        raise SmsError()

    if response.status_code >= 400:
        logger.error("Eskiz: %s", response.text)
        raise SmsError()

def _telegram(phone, code):
    response = requests.post(
        "https://gatewayapi.telegram.org/sendVerificationMessage",
        headers={"Authorization": f"Bearer {settings.TELEGRAM_GATEWAY_TOKEN}"},
        json={"phone_number": f"+{phone}", "code": code, "ttl": 300},
        timeout=10,
    )
    data = response.json()
    if not data.get("ok"):
        logger.error("Telegram Gateway: %s", data.get("error"))
        raise SmsError()
class SmsError(APIException):
    status_code = 503
    default_detail = "SMS yuborib bo'lmadi. Birozdan keyin urinib ko'ring."


def send_code(phone, code):
    backend = settings.SMS_BACKEND

    if backend == "console":
        print(f"[SMS] {phone} -> Tasdiqlash kodingiz: {code}")
    elif backend == "telegram":
        _telegram(phone, code)
    elif backend == "eskiz":
        _eskiz(phone, code)
    else:
        raise SmsError(f"Noma'lum SMS_BACKEND: {backend}")

