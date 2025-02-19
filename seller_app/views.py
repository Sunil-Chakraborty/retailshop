from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from sales.models import Category, Product, Order
from .forms import CategoryForm, ProductForm
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages


# Seller : 9903659749 - Gourav Mazumder

def dashboard(request):
    # Seller dashboard overview
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    return render(request, 'seller_app/dashboard.html', {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
    })

# Category Views
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'seller_app/category_list.html', {'categories': categories})

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('seller_app:category_list')
    else:
        form = CategoryForm()
    return render(request, 'seller_app/category_form.html', {'form': form})

def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('seller_app:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'seller_app/category_form.html', {'form': form})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('seller_app:category_list')
    return render(request, 'seller_app/category_confirm_delete.html', {'category': category})

# Product Views
def product_list(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check for AJAX request
        products = Product.objects.select_related('category').all()
        data = [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": str(product.price),
                "stock": product.stock,
                "category": product.category.name,
                "image_url": product.image.url if product.image else None
            }
            for product in products
        ]
        return JsonResponse({"data": data})
    return render(request, 'seller_app/product_list.html')   
    
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('seller_app:product_list')
    else:
        form = ProductForm()
    return render(request, 'seller_app/product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller_app:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'seller_app/product_form.html', {'form': form})


def product_delete(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return JsonResponse({"success": True, "message": "Product deleted successfully."})
    return JsonResponse({"success": False, "message": "Invalid request method."})

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'seller_app/order_list.html', {'orders': orders})

@require_POST
def edit_order(request):
    order_id = request.POST.get('order_id')
    quantity = request.POST.get('quantity')
    status = request.POST.get('status')

    try:
        order = Order.objects.get(id=order_id)
        order.quantity = quantity
        order.status = status
        order.save()
        messages.success(request, "Order updated successfully!")
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")

    return redirect('seller_app:order_list')

@require_POST
def delete_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.delete()
        messages.success(request, "Order deleted successfully!")
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")

    return redirect('seller_app:order_list')
    