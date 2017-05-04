import logging

from authy.api import AuthyApiClient
from django.conf import settings

from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sportswar.permissions import IsSelfOrSuperuser
from sportswar.users.models import User
from sportswar.users.serializers import UserSerializer


logger = logging.getLogger(__name__)


class UserListView(generics.ListAPIView):
    permission_classes = (permissions.IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,
                          IsSelfOrSuperuser,)

    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.request.data['id']
        return User.objects.filter(id=user_id)


class CurrentUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):  # pylint: disable=no-self-use
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class VerifyPhoneView(APIView):

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        authy_api = AuthyApiClient(settings.AUTHY_KEY)
        authy_user = authy_api.users.create(user.email, user.phone_number, user.country_code)
        if authy_user.ok():
            user.authy_user_id = authy_user.id
            user.save()
            start_check = authy_api.phones.verification_start(user.phone_number, user.country_code, via='sms')
            if start_check.ok():
                return Response('Phone validation started', status=status.HTTP_202_ACCEPTED)
            else:
                logger.warning('Error checking for authy phone number %s', start_check.errors())
                return Response(start_check.errors(), status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.warning('Error checking for authy user %s', authy_user.errors())
            return Response(authy_user.errors(), status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        user = request.user
        authy_api = AuthyApiClient(settings.AUTHY_KEY)
        code = request.data.get('code', '')
        check = authy_api.phones.verification_check(user.phone_number, user.country_code, code)
        if check.ok():
            user.has_validated_phone = True
            user.save()
            return Response('Phone validation complete', status=status.HTTP_200_OK)
        else:
            logger.warning('Authy validation failed %s', check.errors())
            return Response(check.errors(), status=status.HTTP_400_BAD_REQUEST)

