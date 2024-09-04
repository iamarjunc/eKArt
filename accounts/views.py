from email.message import EmailMessage
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from accounts.forms import RegistrationForm,UserForm,UserProfileForm
from accounts.models import Account, UserProfile
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import requests
from django.template.loader import get_template
from xhtml2pdf import pisa
# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from cart.models import Cart, CartItem
from cart.views import _cart_id
from orders.models import Order, OrderProduct

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            
            user = Account.objects.create_user(first_name = first_name,last_name = last_name,email=email,username = username,password= password)
            user.phone_number = phone_number
            user.save()
            
            # Create User Profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = "default/default-user.jpg"
            profile.save()
            
            # User Activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            # messages.success(request,'Thank you for registering with us, We have sent you a verification email to your email address. Please verify it.')

            return redirect(reverse('login') + '?command=verification&email=' + email)
    else:
        form = RegistrationForm()
    context = {
        'form':form
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method=="POST":
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(email=email,password=password)
        print(user)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    # product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                    print('product variations by cart id\n',product_variation)
                        
                    # get the cart items from the user to access his product variations
                    
                    cart_item = CartItem.objects.filter(user = user)
           
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                        
                    print('cart items from the user to access his product variations\n',ex_var_list)
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            
            auth.login(request,user)
            messages.success(request, 'you are now logged in')
            url = request.META.get('HTTP_REFERER')
            print('url')
            print(url)
            try:
                query = requests.utils.urlparse(url).query
                # print("query--->",query)
                # next =/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                # print("params--->",params)
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)         
            except:
                return redirect('dashboard')       
        else:
            messages.error(request, 'invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')    
def logout(request):
    auth.logout(request) 
    messages.success(request, "You are logged out")
    return redirect('login')
    
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
            
        
@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user_id = request.user.id)
    print(orders_count)
    print(userprofile)
    context = {
        'order_count' : orders_count,
        'userprofile' : userprofile
    }
    return render(request, 'accounts/dashboard.html',context)
    

def forgotpassword(request):
    if request.method =='POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact = email)
            # Reset password
            
            
            # User Activation
            current_site = get_current_site(request)
            mail_subject = 'Please reset your Password'
            message = render_to_string('accounts/reset_password.html',{
                'user':user,
                'domain':current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
            
        else:
            messages.error(request, "Account does not exist")
            return redirect('forgotpassword')
    return render(request, 'accounts/forgetpassword.html')


def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your passwprd')
        return redirect('resetpassword')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('login')
    
def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetpassword')
    else:
        return render(request, 'accounts/resetpassword.html')
    
@login_required(login_url='login')    
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders':orders
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='login')
def edit_profile(request):
    print(request.user, '\n')
    print('user profile\n')
    
    # Get or create the UserProfile object
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)
    print(userprofile)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    print("userprofile.profile_picture.url",userprofile.profile_picture)
    print(userprofile.profile_picture.url)
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user = Account.objects.get(username__exact = request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                #  auth.logout(request)
                messages.success(request, "Password updated successfully.")
                return redirect('change_password')
            else:
                messages.error(request, "Please enter valid current password")
                return redirect('change_password')  
        else:
            messages.error(request, 'Password doesnot match')
            return redirect('change_password')
    return render(request,'accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number = order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal
    }
    return render(request, 'accounts/order_detail.html',context)



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def generate_invoice_pdf(request, order_id):
    # Fetch order and related data based on order_id
    order = Order.objects.get(id=order_id)
    order_products = OrderProduct.objects.filter(order=order)

    context = {
        'order': order,
        'order_products': order_products,
        'subtotal': sum([op.product_price * op.quantity for op in order_products]),  # Calculate subtotal
    }

    pdf = render_to_pdf('invoice_template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Invoice_{order.order_number}.pdf"
        content = f"inline; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("PDF could not be generated")