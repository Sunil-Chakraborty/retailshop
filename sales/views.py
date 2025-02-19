from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, Customer, Category
from decimal import Decimal
from django.http import JsonResponse
from django.db.models import Sum, F, FloatField
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings  # Import for MEDIA_URL
from django.core.exceptions import ValidationError
from .forms import CustomerForm

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

import os
from django.contrib.staticfiles import finders

#https://www.flipkart.com/pens-stationery/office-supplies/card-holders/pr?sid=dgv,tkw,chd&p[]=facets.serviceability%5B%5D%3Dtrue&otracker=categorytree&otracker=nmenu_sub_Sports%2C%20Books%20%26%20More_0_Card%20Holders

def check_customer(request):
    mobile_number = request.GET.get('mobile_number', '').strip()

    # Validate mobile number length
    if not mobile_number or len(mobile_number) != 10 or not mobile_number.isdigit():
        return JsonResponse({
            'exists': False,
            'error': 'Valid 10-digit mobile number is required.'
        })

    # Check if customer exists
    customer = Customer.objects.filter(mobile_number=mobile_number).first()

    if customer:
        return JsonResponse({
            'exists': True,
            'name': customer.name,
            'address': customer.address,
        })

    return JsonResponse({'exists': False})
    
        
def ask_mobile_number(request):
    if request.method == 'POST':
        
        # Get the entered mobile number
        mobile_number = request.POST.get('mobile_number')
        
        # Check if the mobile number exists in the Customer table
        customer = Customer.objects.filter(mobile_number=mobile_number).first()

        if customer:
            # If customer exists, use the data from the database
            request.session['mobile_number'] = customer.mobile_number
            request.session['customer_name'] = customer.name
            request.session['customer_address'] = customer.address
        else:
            # If customer doesn't exist, get the entered name and address
            name = request.POST.get('name')
            address = request.POST.get('address')
            request.session['mobile_number'] = mobile_number
            request.session['customer_name'] = name
            request.session['customer_address'] = address
            
            Customer.objects.create(
                    mobile_number=mobile_number,
                    name=name,
                    address=address,
                    
                )
        if (mobile_number == "1111111111"):
            return redirect('seller_app:dashboard')  # Redirect to product list page
        else:
            return redirect('sales:product_list')  # Redirect to product list page

    return render(request, 'sales/ask_mobile_number.html')
    
def product_list(request):
    # Get customer details from the session
    mobile_number = request.session.get('mobile_number')
    customer_name = request.session.get('customer_name')
    customer_address = request.session.get('customer_address')

    # Get the selected category from the GET parameter
    category_id = request.GET.get('category', None)

    # Fetch all categories for the dropdown
    categories = Category.objects.all()

    # Filter products by category if selected, otherwise show all products
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    # Get cart details
    cart_count = Order.objects.filter(mobile_number=mobile_number).count()
    total_quantity = Order.objects.filter(mobile_number=mobile_number).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Render the template and pass the products and categories
    return render(request, 'sales/product_list.html', {
        'products': products,
        'cart_count': cart_count,
        'categories': categories,
        'mobile_number': mobile_number,
        'customer_name': customer_name,
        'customer_address': customer_address,
        'selected_category': int(category_id) if category_id else None,
    })

def place_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    mobile_number = request.session.get('mobile_number')
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        # Use consistent session key
        cart_key = f'cart_{mobile_number}'
        cart = request.session.get(cart_key, {})
        print("Before Adding to Cart:", cart)

        if str(product.id) in cart:
            cart[str(product.id)]['quantity'] += quantity
        else:
            cart[str(product.id)] = {
                'name': product.name,
                'price': str(product.price),
                'quantity': quantity,
            }
        
        request.session[cart_key] = cart  # Save updated cart in session
        request.session.modified = True  # Ensure session changes are saved
        print("After Adding to Cart:", request.session.get(cart_key))
        
        #return redirect('sales:view_cart')
        # Redirect to the finalize_order action
        return HttpResponseRedirect(reverse('sales:finalize_order'))

    return render(request, 'sales/place_order.html', {'product': product, 'mobile_number': mobile_number})

def order_confirmation(request):
    # Get the mobile number from the session
    mobile_number = request.session.get('mobile_number')
    customer_name = request.session.get('customer_name')
    customer_address = request.session.get('customer_address')
    
    # Fetch the orders associated with the current mobile number
    orders = Order.objects.filter(mobile_number=mobile_number).order_by('-date')

    # Calculate the total amount for the current order
    total_amount = sum(order.total_price for order in orders)

    return render(request, 'sales/order_confirmation.html', {
        'mobile_number': mobile_number,
        'customer_name': customer_name,
        'customer_address' : customer_address,
        'orders': orders,
        'total_amount': total_amount,
    })
    

# Add a product to the cart
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    mobile_number = request.session.get('mobile_number')
    quantity = int(request.POST.get('quantity', 1))

    cart_key = f'cart_{mobile_number}'
    cart = request.session.get(cart_key, {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': quantity,
        }

    request.session[cart_key] = cart

    # Send WebSocket notification to seller
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "seller_notifications",  # The WebSocket group name
        {
            "type": "send_notification",
            "message": f"New Order: {product.name} (Qty: {quantity})"
        }
    )

    return JsonResponse({'message': 'Added to cart successfully!'})

  
# View and finalize the cart

def view_cart(request):
    mobile_number = request.session.get('mobile_number')

    if not mobile_number:
        return redirect('sales:ask_mobile_number')  # Redirect if no mobile number is in the session

    # Query the Order table for the current mobile number and aggregate products
    orders = (
        Order.objects.filter(mobile_number=mobile_number)
        .values('product', 'status')  # Include 'status' in the grouping
        .annotate(            
            product_name=F('product__name'),
            product_image=F('product__image'),  # Get file path for the image
            price=F('product__price'),
            total_quantity=Sum('quantity'),
            total_subtotal=Sum(F('product__price') * F('quantity'), output_field=FloatField())
        )
    )
     

    # Prepare the cart data with aggregated information
    
    cart = [
        {
            'product_id': order['product'],
            'product_name': order['product_name'],
            'product_image_url': f"{settings.MEDIA_URL}{order['product_image']}" if order['product_image'] else None,
            'price': order['price'],            
            'quantity': order['total_quantity'],
            'subtotal': order['total_subtotal'],
            'status': order['status'],
        }
        for order in orders
    ]
    
    # Calculate the total cost and total quantity
    total = sum(item['subtotal'] for item in cart)
    qty = sum(item['quantity'] for item in cart)

    # Render the cart template with the aggregated data
    return render(request, 'sales/view_cart.html', {
        'cart': cart,
        'total': total,
        'qty': qty,        
        'mobile_number': mobile_number,  # Pass mobile_number to the template
    })

# Finalize the order
def finalize_order(request):
    customer_mobile = request.session.get("mobile_number")
    if not customer_mobile:
        return redirect("sales:view_cart")

    customer = Customer.objects.filter(mobile_number=customer_mobile).first()
    cart = request.session.get(f"cart_{customer_mobile}", {})

    if not cart:
        return redirect("sales:view_cart")

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        quantity = item["quantity"]
        total_price = Decimal(item["price"]) * quantity

        Order.objects.create(
            mobile_number=customer_mobile,
            customer=customer,
            product=product,
            quantity=quantity,
            total_price=total_price,
        )

    # Clear the cart after placing the order
    request.session[f"cart_{customer_mobile}"] = {}

    # Send WebSocket notification to the seller
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "seller_notifications",
        {"type": "send_notification", "message": f"New Order from {customer_mobile}"}
    )

    return redirect("sales:order_confirmation")
    

def update_cart(request):
    if request.method == 'POST':
        mobile_number = request.session.get('mobile_number')

        # Iterate through submitted data
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                counter = key.split('_')[1]
                product_id = request.POST.get(f'product_id_{counter}')
                quantity = int(value)

                # Update the order in the database
                order = Order.objects.filter(mobile_number=mobile_number, product_id=product_id).first()
                if order:
                    order.quantity = quantity
                    order.total_price = Decimal(order.product.price) * quantity
                    order.save()

        return redirect('sales:view_cart')
        
def delete_cart_item(request, product_id):
    mobile_number = request.session.get('mobile_number')
    
    # Delete the order associated with the product and mobile number
    Order.objects.filter(mobile_number=mobile_number, product_id=product_id).delete()
    
    return redirect('sales:view_cart')


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access them.
    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = finders.find(uri.replace(settings.STATIC_URL, ""))
    else:
        path = uri  # Return the original URI if not static or media

    if not os.path.isfile(path):
        raise Exception(f"File not found: {path}")
    return path

def generate_order_pdf(request):
    mobile_number = request.session.get('mobile_number')
    customer_name = request.session.get('customer_name', "Unknown")
    customer_address = request.session.get('customer_address', "Unknown")

    # Query the orders for the current customer
    orders = Order.objects.filter(mobile_number=mobile_number)
    total_amount = sum(order.total_price for order in orders)

    # Render the HTML template with order details
    html_content = render_to_string('sales/order_confirmation.html', {
        'mobile_number': mobile_number,
        'customer_name': customer_name,
        'customer_address': customer_address,
        'orders': orders,
        'total_amount': total_amount,
        'for_pdf': True,
    })

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="order_{mobile_number}.pdf"'
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=result, link_callback=link_callback)

    if not pdf.err:
        response.write(result.getvalue())
        return response
    else:
        return HttpResponse("Error generating PDF", status=500)
