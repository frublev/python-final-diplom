from django.contrib import admin
from .models import User, ConfirmEmailToken, Contact


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

    list_display = ('id', 'user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone')
