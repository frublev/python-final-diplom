from django.contrib import admin
from .models import User, ConfirmEmailToken, Contact, Shop, File, Category, Product, ProductInfo, ProductParameter


@admin.register(File)
class FileAdmin(admin.ModelAdmin):

    model = File


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    model = User

    fieldsets = (
        (None, {'fields': ('email', 'password', 'type')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('id', 'email', 'username', 'first_name', 'last_name', 'type', 'is_active', 'is_staff')


@admin.register(ConfirmEmailToken)
class ConfirmTokenAdmin(admin.ModelAdmin):

    model = ConfirmEmailToken

    list_display = ('id', 'user', 'token', 'created_at')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):

    model = Contact

    list_display = ('id', 'user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone', 'url')


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):

    model = Shop

    list_display = ('id', 'user', 'name', 'state')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    model = Category

    list_display = ('id', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    model = Product

    list_display = ('id', 'name', 'category')


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):

    model = ProductInfo

    list_display = ('id', 'model', 'external_id', 'product', 'shop', 'quantity', 'price', 'price_rrc')


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):

    model = ProductParameter

    list_display = ('id', 'product_info', 'parameter', 'value')

