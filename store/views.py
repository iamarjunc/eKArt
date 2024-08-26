from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from cart.models import CartItem
from cart.views import _cart_id
from category.models import Category
from orders.models import OrderProduct
from store.forms import ReviewForm
from store.models import Product, ProductGallery, ReviewRating, Variation
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
from django.db.models import Count, Avg
# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    # Filter by category if provided
    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)

    # Filtering by color, size, and price range
    selected_colors = request.GET.getlist('color') if 'color' in request.GET else []
    selected_sizes = request.GET.getlist('size') if 'size' in request.GET else []
    min_price = request.GET.get('min_price') if 'min_price' in request.GET else None
    max_price = request.GET.get('max_price') if 'max_price' in request.GET else None
    sort_option = request.GET.get('sort', '')

    if selected_colors:
        products = products.filter(variation__variation_category='color', variation__variation_value__in=selected_colors).distinct()

    if selected_sizes:
        products = products.filter(variation__variation_category='size', variation__variation_value__in=selected_sizes).distinct()

    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    # Sorting
    if sort_option == 'price_low_to_high':
        products = products.order_by('price')
    elif sort_option == 'price_high_to_low':
        products = products.order_by('-price')
    elif sort_option == 'popularity':
        products = products.annotate(review_count=Count('reviewrating')).order_by('-review_count')
    
    # Pagination
    paginator = Paginator(products, 3)  # Change the number to adjust items per page
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    # Fetch available colors and sizes for the filter
    available_colors = Variation.objects.filter(variation_category='color').values_list('variation_value', flat=True).distinct()
    available_sizes = Variation.objects.filter(variation_category='size').values_list('variation_value', flat=True).distinct()

    context = {
        'products': paged_products,
        'product_count': product_count,
        'available_colors': available_colors,
        'available_sizes': available_sizes,
        'selected_colors': selected_colors,
        'selected_sizes': selected_sizes,
        'selected_min_price': min_price,
        'selected_max_price': max_price,
        'sort_option': sort_option,  # Add this to maintain the selected sort option in the template
    }
    return render(request, 'store/store.html', context)


def product_detail(request,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug = category_slug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product = single_product).exists()
        
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user = request.user, product_id = single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
        
    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id = single_product.id, status = True)
    #  USER IMAGE
    
    # Get the Product Gallery
    product_gallery = ProductGallery.objects.filter(product_id = single_product.id)
        
    context = {
        'single_product' : single_product,
        'in_cart' : in_cart,
        'orderproduct' : orderproduct,
        'reviews' : reviews,
        'product_gallery' : product_gallery,
    }
    return render(request, 'store/product_detail.html',context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(decription__icontains = keyword) | Q(product_name__icontains = keyword))
            product_count = products.count()
            
        context = {
            'products':products,
            'product_count' : product_count,
        }
    return render(request,'store/store.html',context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, "Thank You! Your review has been submitted")
                return redirect(url)