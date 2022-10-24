from distutils.util import strtobool
import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q, Sum, F
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError

from requests import get
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from yaml import load as load_yaml, Loader

from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .delivery_price import delivery_price
from .messege_manager import send_email
from .models import User, ConfirmEmailToken, Contact, Shop, Category, ProductInfo, Product, Parameter, \
    ProductParameter, Order, OrderItem
from .serializers import UserSerializer, ContactSerializer, OrderSerializer, OrderItemSerializer, ProductInfoSerializer, \
    CategorySerializer, ShopSerializer, ProductSerializer
from purchase_service.settings import DEFAULT_FROM_EMAIL

from .signals import new_order, confirm_order


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
                receivers = [request.data['email']]
                send_email(email_subject, email_html, receivers)
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


class AccountDetails(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if 'password' in request.data:
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                request.user.set_password(request.data['password'])

        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


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
        items_ = request.data.get('items')
        if items_:
            items_list = items_.split(',')
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


class ShopState(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'For shops only'}, status=403)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'For shops only'}, status=403)
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=strtobool(state))
                return JsonResponse({'Status': True})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})
        return JsonResponse({'Status': False, 'Errors': 'Something went wrong'})


class ShopUpdate(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'For shops only'}, status=403)

        url = request.data.get('url')
        now = datetime.datetime.now()
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                stream = get(url).content
                data = load_yaml(stream, Loader=Loader)
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                    shop_id = request.user.shop.id
                    category_object.shops.add(shop_id)
                    category_object.save()
                # ProductInfo.objects.filter(shop_id=shop_id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
                    product_info = ProductInfo.objects.filter(
                        product_id=product.id,
                        external_id=item['id'],
                        shop_id=shop_id,
                        state='new')
                    if product_info:
                        duplicate = True
                    else:
                        duplicate = False
                    product_info_new = ProductInfo.objects.create(product_id=product.id,
                                                                  external_id=item['id'],
                                                                  model=item['model'],
                                                                  description=item['description'],
                                                                  price=item['price'],
                                                                  price_rrc=item['price_rrc'],
                                                                  quantity=item['quantity'],
                                                                  shop_id=shop_id,
                                                                  update_time=now,
                                                                  weight=item['weight'],
                                                                  package=item['package'],
                                                                  state='new')
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info_new.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)
                    if duplicate:
                        print(product_info[0])
                        product_info_old = ProductInfoSerializer(product_info[0]).data
                        old_id = product_info_old.pop('id')
                        product_info_old.pop('quantity')
                        print(product_info_old)
                        product_info_new = ProductInfoSerializer(product_info_new).data
                        new_id = product_info_new.pop('id')
                        quantity_new = product_info_new.pop('quantity')
                        print(product_info_new)
                        if product_info_new == product_info_old:
                            print(quantity_new)
                            deleted_count = ProductInfo.objects.filter(id=new_id).delete()[0]
                            ProductInfo.objects.filter(id=old_id).update(quantity=quantity_new)
                        else:
                            ProductInfo.objects.filter(id=old_id).update(state='old')

                return JsonResponse({'Status': True})
        return JsonResponse({'Status': False, 'Errors': 'Something went wrong'})


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductView(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductSearch(ListAPIView):
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    filter_backends = [SearchFilter]
    search_fields = ['product__name']


class CatalogView(APIView):
    def get(self, request):
        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')
        if shop_id:
            query = query & Q(shop_id=shop_id)
        if category_id:
            query = query & Q(product__category_id=category_id)
        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()
        serializer = ProductInfoSerializer(queryset, many=True)
        return Response(serializer.data)


class BasketView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(basket, many=True)
        order_response = serializer.data
        delivery_sum = delivery_price(order_response[0]['ordered_items'])
        print(delivery_sum)
        total_sum = order_response[0]['total_sum'] + delivery_sum
        order_response[0].update({'стоимость доставки': delivery_sum, 'итого': total_sum})
        return Response(order_response)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_ = request.data.get('items')
        if items_:
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            objects_created = 0
            for order_item in items_:
                order_item.update({'order': basket.id})
                serializer = OrderItemSerializer(data=order_item)
                if serializer.is_valid():
                    try:
                        serializer.save()
                    except IntegrityError as error:
                        return JsonResponse({'Status': False, 'Errors': str(error)})
                    else:
                        objects_created += 1

                else:
                    JsonResponse({'Status': False, 'Errors': serializer.errors})

            return JsonResponse({'Status': True, 'Objects created': objects_created})
        return JsonResponse({'Status': False, 'Errors': 'Items missing'})

    def delete(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_ = request.data.get('items')
        if items_:
            items_list = items_.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Objects deleted': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Items missing'})

    def put(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        items_ = request.data.get('items')
        if items_:
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            objects_updated = 0
            for order_item in items_:
                if type(order_item['id']) == int and type(order_item['quantity']) == int:
                    objects_updated += OrderItem.objects.filter(order_id=basket.id,
                                                                id=order_item['id']).update(
                        quantity=order_item['quantity'])
            return JsonResponse({'Status': True, 'Objects updated': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Items missing'})


class OrderUserView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        order = Order.objects.filter(
            user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    def patch(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        state = request.data.get('state')
        contact = request.data.get('contact')
        if state == 'new' and contact:
            order = Order.objects.filter(user_id=request.user.id, state='basket')
            order_id = order.first().id
            order_updated = order.update(state='new', contact=contact)
            OrderItem.objects.filter(order=order_id).update(state='new')
            if not order_updated:
                return JsonResponse({'Status': False, 'Errors': 'Basket is empty'})
            else:
                new_order.send(sender=self.__class__, signal_data={'user_id': request.user.id, 'order_id': order_id})
                order = Order.objects.filter(
                    id=order_id).prefetch_related(
                    'ordered_items__product_info__product__category',
                    'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
                    total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
                serializer = OrderSerializer(order, many=True)
                return Response(serializer.data)
        return JsonResponse({'Status': False, 'Errors': 'Incorrect request'})


class OrderShopView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        order_id = request.data.get('order_id')
        items_ = request.data.get('items')
        if items_:
            items_list = items_.split(',')
            objects_updated = 0
            for order_item in items_list:
                objects_updated += OrderItem.objects.filter(order_id=order_id,
                                                            id=order_item,
                                                            state='new').update(state='confirmed')
            order_item = OrderItem.objects.filter(order_id=order_id, state='new')
            if not order_item:
                order = Order.objects.filter(id=order_id)
                user_id = order[0].user.id
                confirm_order.send(sender=self.__class__, signal_data={'user_id': user_id,
                                                                       'order_id': order_id})
            return JsonResponse({'Status': True, 'Objects updated': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Items missing'})
