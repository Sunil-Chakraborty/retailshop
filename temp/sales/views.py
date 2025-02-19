from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, Customer, Category
from decimal import Decimal
from django.http import JsonResponse

from django.shortcuts import render, redirect
from .models import Customer

#https://www.flipkart.com/pens-stationery/office-supplies/card-holders/pr?sid=dgv,tkw,chd&p[]=facets.serviceability%5B%5D%3Dtrue&otracker=categorytree&otracker=nmenu_sub_Sports%2C%20Books%20%26%20More_0_Card%20Holders

def check_customer(request):
    mobile_number = request.GET.get('mobile_number', '')
    customer = Customer.objects.filter(mobile_number=mobile_number).first()

    if customer:
        return JsonResponse({
            'exists': True,
            'name': customer.name,
            'address': customer.address,
        })
    else:
        return JsonResponse({'exists': False})
        
        
def ask_mobile_number(request):
    customer_data = {
        'name': '',
        'address': '',
        'shop_name': 'Village Shop'
    }

    if request.method == 'POST':
        # Get the entered mobile number, name, and address from the request
        mobile_number = request.POST.get('mobile_number')
        name = request.POST.get('name')
        address = request.POST.get('address')

        # Check if the mobile number exists in the Customer table
        customer = Customer.objects.filter(mobile_number=mobile_number).first()

        if customer:
            # If customer exists, pre-fill the name and address
            customer_data['name'] = customer.name
            customer_data['address'] = customer.address
        else:
            # If customer does not exist, create a new customer
            customer = Customer.objects.create(
                name=name,
                mobile_number=mobile_number,
                address=address
            )

        # Store the details in the session
        request.session['mobile_number'] = customer.mobile_number
        request.session['customer_name'] = customer.name
        request.session['customer_address'] = customer.address

        return redirect('sales:product_list')  # Redirect to the product list page

    return render(request, 'sales/ask_mobile_number.html', customer_data)
    
    
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

    # Render the template and pass the products and categories
    return render(request, 'sales/product_list.html', {
        'products': products,
        'categories': categories,
        'mobile_number': mobile_number,
        'customer_name': customer_name,
        'customer_address': customer_address,
        'selected_category': int(category_id) if category_id else None,
    })
    
    
def place_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    mobile_number = request.session.get('mobile_number')
    customer_name = request.session.get('customer_name')
    customer_address = request.session.get('customer_address')

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        total_price = product.price * quantity

        # Create or get the customer using the mobile number
        customer, created = Customer.objects.get_or_create(
            mobile_number=mobile_number,
            defaults={'name': customer_name, 'address': customer_address}
        )

        # Create the order
        Order.objects.create(
            customer=customer,
            product=product,
            quantity=quantity,
            total_price=total_price,
            mobile_number=mobile_number,
        )

        return redirect('sales:order_confirmation')  # Redirect to confirmation page

    return render(request, 'sales/place_order.html', {'product': product, 'mobile_number': mobile_number})

def order_confirmation(request):
    # Get the mobile number from the session
    mobile_number = request.session.get('mobile_number')

    # Fetch the orders associated with the current mobile number
    orders = Order.objects.filter(mobile_number=mobile_number).order_by('-date')

    # Calculate the total amount for the current order
    total_amount = sum(order.total_price for order in orders)

    return render(request, 'sales/order_confirmation.html', {
        'mobile_number': mobile_number,
        'orders': orders,
        'total_amount': total_amount,
    })
    
# Seller Panel: Display all products with an "Add to Cart" option
def seller_panel(request):
    products = Product.objects.all()
    cart = request.session.get('cart', {})
    return render(request, 'seller_panel.html', {'products': products, 'cart': cart})

# Add a product to the cart
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Initialize cart in session if not already present
    cart = request.session.get('cart', {})

    # Add product to the cart
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': quantity,
        }

    request.session['cart'] = cart
    return redirect('seller_panel')
    
# View and finalize the cart
def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
    customers = Customer.objects.all()
    return render(request, 'sales/view_cart.html', {'cart': cart, 'total': total, 'customers': customers})


# Finalize the order
def finalize_order(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        customer = get_object_or_404(Customer, id=customer_id)
        cart = request.session.get('cart', {})

        # Create orders for each item in the cart
        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            quantity = item['quantity']
            total_price = Decimal(item['price']) * quantity
            Order.objects.create(
                customer=customer,
                product=product,
                quantity=quantity,
                total_price=total_price,
                mobile_number=customer.mobile_number,
            )

        # Clear the cart
        request.session['cart'] = {}
        return redirect('order_confirmation')  # Redirect to a confirmation page

    return redirect('view_cart')
 
