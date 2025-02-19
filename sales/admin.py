from django.contrib import admin
from .models import Product, Customer, Order, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name', 'description')


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0  # No empty rows by default

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'mobile_number', 'address')
    search_fields = ('name', 'mobile_number')
    inlines = [OrderInline]  # Add inline orders


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile_number', 'product', 'quantity', 'total_price', 'status', 'date')
    actions = ['mark_as_processed']

    def mark_as_processed(self, request, queryset):
        queryset.update(is_processed=True)
        self.message_user(request, "Selected orders have been marked as processed.")
    mark_as_processed.short_description = "Mark selected orders as processed"

