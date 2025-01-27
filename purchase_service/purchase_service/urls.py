"""purchase_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from backend.views import AllUserView, CreateUser, UserAuth, confirm_email, ContactView, AllContactView, \
    ShopUpdate, BasketView, AccountDetails, CatalogView, CategoryView, ShopView, ProductSearch, OrderUserView, \
    ShopState, OrderShopView, ProductView
from rest_framework.routers import DefaultRouter

from purchase_service import settings


router = DefaultRouter()
router.register('products', ProductView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', AllUserView.as_view()),
    path('account/', AccountDetails.as_view()),
    path('create_user/', CreateUser.as_view()),
    path('login/', UserAuth.as_view()),
    path('confirm_email/', confirm_email),
    path('contacts/', ContactView.as_view()),
    path('all_contacts/', AllContactView.as_view()),
    path('update_price/', ShopUpdate.as_view()),
    path('categories/', CategoryView.as_view()),
    path('shops/', ShopView.as_view()),
    path('shops_state/', ShopState.as_view()),
    path('catalog/', CatalogView.as_view()),
    path('product_search/', ProductSearch.as_view()),
    path('basket/', BasketView.as_view()),
    path('user_orders/', OrderUserView.as_view()),
    path('shop_orders/', OrderShopView.as_view()),
] + router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
