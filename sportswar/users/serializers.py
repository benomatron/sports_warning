from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

from sportswar.events.models import Watcher
from sportswar.users.models import User


class UserSerializer(serializers.ModelSerializer):
    watchers = serializers.PrimaryKeyRelatedField(many=True, queryset=Watcher.objects.all())

    class Meta:
        model = User
        fields = ('id', 'email', 'is_staff', 'display_name', 'is_superuser', 'is_active',
                  'watchers', 'phone_number', 'has_validated_phone', 'time_zone')


class CustomRegisterSerializer(RegisterSerializer):  # pylint: disable=abstract-method
    time_zone = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True, allow_blank=True)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
            'time_zone': self.validated_data.get('time_zone', '')
        }

    def custom_signup(self, request, user):
        time_zone = self.cleaned_data.get('time_zone', '')
        phone_number = self.cleaned_data.get('phone_number', '')
        if time_zone:
            user.time_zone = time_zone
        if phone_number:
            user.phone_number = phone_number
        user.save()

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()  # pylint: disable=attribute-defined-outside-init
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
