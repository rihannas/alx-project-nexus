import django_filters
from .models import Product, ProductVariant

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category__slug')
    min_price = django_filters.NumberFilter(field_name='variants__price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='variants__price', lookup_expr='lte')
    size = django_filters.CharFilter(field_name='variants__size')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'status', 'min_price', 'max_price', 'size', 'in_stock']
    
    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(variants__inventory_quantity__gt=0).distinct()
        return queryset
