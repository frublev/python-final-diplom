from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives

from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from .models import User, ConfirmEmailToken
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
                email_confirm_token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user.id)
                email = [request.data['email']]
                email_html = f'<p>To confirm e-mail click <a href="http://127.0.0.1:8000/confirm_email?token=' \
                             f'{email_confirm_token.token}">here</a>.</p>'
                sending_mail = EmailMultiAlternatives(
                    'Registration',
                    email_html,
                    DEFAULT_FROM_EMAIL,
                    email
                )
                sending_mail.attach_alternative(email_html, "text/html")
                sending_mail.send()
                return JsonResponse({'Status': True, 'email_confirm_token': email_confirm_token.token})
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


def confirm_email(request):
    token = request.GET.get('token')
    token_in_db = ConfirmEmailToken.objects.filter(token=token).first()
    if token_in_db:
        token_in_db.user.is_active = True
        token_in_db.user.save()
        username = token_in_db.user
        token_in_db.delete()
        return HttpResponse(f'E-mail of user {username} has confirmed')
