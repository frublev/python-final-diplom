from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives

from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .messege_manager import send_email
from .models import User, ConfirmEmailToken, Contact, Shop
from .serializers import UserSerializer, ContactSerializer
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
                user_type = request.data.get('type')
                if user_type == 'shop':
                    shop, _ = Shop.objects.get_or_create(user=user, name=request.data['company'], state=False)
                email_subject = 'Registration'
                email_confirm_token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user.id)
                email_html = f'<p>To confirm e-mail click <a href="http://127.0.0.1:8000/confirm_email?token=' \
                             f'{email_confirm_token.token}">here</a>.</p>'
                sender = DEFAULT_FROM_EMAIL
                receivers = [request.data['email']]
                send_email(email_subject, email_html, sender, receivers)
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
        if token_in_db.user.type == 'shop':
            token_in_db.user.shop.state = True
            token_in_db.user.shop.save()
        username = token_in_db.user
        token_in_db.delete()
        return HttpResponse(f'E-mail of user {username} has confirmed')


class AllContactView(ListAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class ContactView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'You are not authorized'}, status=403)
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'You are not authorized'}, status=403)
        if {'city', 'street', 'phone', 'house'}.issubset(request.data):
            request.data.update({'user': request.user.id})
            print(request.data)
            serializer = ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                JsonResponse({'Status': False, 'Errors': serializer.errors})
        return JsonResponse({'Status': False, 'Errors': 'Оne or more required fields are not filled'})

    def delete(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        items_string = request.data.get('items')
        if items_string:
            items_list = items_string.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True
            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Objects deleted': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Something went wrong'})

    def put(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
                print(contact)
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'Status': True})
                    else:
                        JsonResponse({'Status': False, 'Errors': serializer.errors})
        return JsonResponse({'Status': False, 'Errors': 'Something went wrong'})
