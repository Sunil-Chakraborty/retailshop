from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.ask_mobile_number, name='ask_mobile_number'),  # Homepage to enter mobile number
    path('products/', views.product_list, name='product_list'),  # Product list with category filtering
    path('place-order/<int:product_id>/', views.place_order, name='place_order'),  # Product details and order form
    path('view-cart/', views.view_cart, name='view_cart'),  # View cart page
    path('finalize-order/', views.finalize_order, name='finalize_order'),  # Finalize the order
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('sales/check-customer/', views.check_customer, name='check_customer'),

]

