from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from django.core.mail import send_mail

from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer
from purchase_service.settings import DEFAULT_FROM_EMAIL


class AllUserView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CreateUser(APIView):
    def post(self, request):
        try:
            validate_password(request.data['password'])
        except Exception as password_error:
            error_array = []
            for item in password_error:
                error_array.append(item)
            return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
        else:
            user_serializer = UserSerializer(data=request.data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                user.set_password(request.data['password'])
                user.save()
                send_mail(
                    'Registration',
                    'You are registered',
                    DEFAULT_FROM_EMAIL,
                    [request.data['email']],
                    fail_silently=False,
                )
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class UserAuth(APIView):
    def post(self, request):
        user = authenticate(username=request.data['email'], password=request.data['password'])
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({'Status': 'You are authorized', 'Token': token.key})
        else:
            return JsonResponse({'Status': 'You are not authorized'})
