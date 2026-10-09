from datetime import timedelta

from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app.models import User, PhoneCode
from app.serializers import (
    RegisterSerializer,
    VerifyPhoneSerializer,
    ResendCodeSerializer
)
from app.services import send_verification_code
from app.sms import SmsError


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        try:
            send_verification_code(user)
        except SmsError:
            user.delete()
            raise


class VerifyPhoneView(generics.GenericAPIView):
    serializer_class = VerifyPhoneSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            phone=serializer.validated_data["phone"],
            is_active=False
        ).first()

        record = PhoneCode.objects.filter(user=user).first()

        if record is None or record.is_expired():
            return Response(
                {"detail": "Kod topilmadi yoki muddati tugagan"},
                status=400
            )

        if record.attempts >= PhoneCode.MAX_ATTEMPTS:
            return Response(
                {"detail": "Urinishlar tugadi, yangi kod so'rang"},
                status=400
            )

        if record.code != serializer.validated_data["code"]:
            record.attempts += 1
            record.save()

            return Response(
                {"detail": "Kod noto'g'ri"},
                status=400
            )

        user.is_active = True
        user.save()

        record.delete()

        return Response(
            {"detail": "Raqam tasdiqlandi. Endi login qiling."}
        )


class ResendCodeView(generics.GenericAPIView):
    serializer_class = ResendCodeSerializer
    permission_classes = [AllowAny]

    RESEND_INTERVAL = timedelta(seconds=60)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            phone=serializer.validated_data["phone"],
            is_active=False
        ).first()

        if user:
            record = PhoneCode.objects.filter(user=user).first()

            if record and timezone.now() - record.created_at < self.RESEND_INTERVAL:
                return Response(
                    {"detail": "1 daqiqada faqat 1 marta"},
                    status=429
                )

            try:
                send_verification_code(user)
            except SmsError:
                return Response(
                    {"detail": "SMS yuborishda xatolik"},
                    status=400
                )

        return Response(
            {
                "detail": "Agar bunday raqam ro'yxatdan o'tgan bo'lsa, "
                "kod yuborildi"
            }
        )