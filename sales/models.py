from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name
        

class Customer(models.Model):
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=10, unique=True)  # Ensure max length is 10
    address = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.mobile_number})"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(mobile_number__regex=r'^\d{10}$'),  # Regular expression to ensure exactly 10 digits
                name='valid_mobile_number',  # Constraint name
            )
        ]       
        
class Order(models.Model):
    mobile_number   = models.CharField(max_length=15)  # Captured at order time
    customer        = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    product         = models.ForeignKey(Product, on_delete=models.CASCADE)
    STS_CHOICES = (
 		 ('', 'Select'),
         ('Pending', 'Pending'),
         ('Delivered', 'Delivered'),
         ('Cancelled', 'Cancelled'),
         ('No Stock', 'No Stock'),
         
	)
    status          = models.CharField(verbose_name='Order Status', max_length=15,
                      choices=STS_CHOICES, null=True, blank=True, default="Pending")
    quantity        = models.PositiveIntegerField()
    total_price     = models.DecimalField(max_digits=10, decimal_places=2)
    date            = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.mobile_number}"
