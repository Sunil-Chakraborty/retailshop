from django.urls import path
from . import views


app_name = 'seller_app'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_add'),
    path('products/<int:pk>/edit/', views.product_update, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('orders/', views.order_list, name='order_list'),
    path('edit_order/', views.edit_order, name='edit_order'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
]
