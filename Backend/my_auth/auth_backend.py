from django.contrib.auth.backends import ModelBackend
from .models import User

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, phone_number=None, password=None, **kwargs):
        try:
            if email:
                user = User.objects.get(email=email)
            elif phone_number:
                user = User.objects.get(phone_number=phone_number)
            elif username:
                user = User.objects.get(username=username)
            else:
                return None

            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
