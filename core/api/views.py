# fake_sms/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
)

from core.services.otp_store import OTPStoreService


class SendOTPAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        serializer = SendOTPSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        OTPStoreService.save(
            serializer.validated_data["mobile"],
            serializer.validated_data["otp"],
        )

        return Response(
            {"success": True},
            status=status.HTTP_200_OK,
        )


class VerifyOTPAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        serializer = VerifyOTPSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        success = OTPStoreService.verify(
            serializer.validated_data["mobile"],
            serializer.validated_data["otp"],
        )

        return Response(
            {
                "success": success
            },
            status=status.HTTP_200_OK,
        )