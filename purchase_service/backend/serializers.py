from rest_framework import serializers
from .models import User, Contact, Order, OrderItem, Shop, Product, ProductParameter, ProductInfo, Category


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'patronymic', 'last_name', 'email', 'company', 'position', 'type')
        read_only_fields = ('id', )


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = ('id', 'user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone', 'url')
        read_only_fields = ('id', )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state',)
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'category',)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'description', 'product', 'shop', 'external_id', 'quantity', 'price', 'price_rrc',
                  'weight', 'package', 'product_parameters',)
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product_info', 'quantity')
        read_only_fields = ('id', )


class ProductInBasketSerializer(serializers.ModelSerializer):
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('model', 'product', 'shop', 'external_id', 'price', 'weight', 'package', 'product_parameters',)
        read_only_fields = ('id',)


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInBasketSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)
    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'dt', 'ordered_items', 'total_sum', 'state', 'contact')
        read_only_fields = ('id', )
