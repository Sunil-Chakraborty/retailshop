from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.ask_mobile_number, name='ask_mobile_number'),  # Homepage to enter mobile number
    path('products/', views.product_list, name='product_list'),  # Product list with category filtering
    path('place-order/<int:product_id>/', views.place_order, name='place_order'),  # Product details and order form
    path('view-cart/', views.view_cart, name='view_cart'),  # View cart page
    path('update-cart/', views.update_cart, name='update_cart'),
    path('delete-cart-item/<int:product_id>/', views.delete_cart_item, name='delete_cart_item'), 
    path('finalize-order/', views.finalize_order, name='finalize_order'),  # Finalize the order
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('check-customer/', views.check_customer, name='check-customer'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('order-pdf/', views.generate_order_pdf, name='generate_order_pdf'),

]

