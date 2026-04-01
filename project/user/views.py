from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User,Group
from .models import *
from .models import Cartitems,Order,review
from manager.models import Product,Category
from django.contrib import messages
from django.contrib.auth import authenticate,login,get_user_model
import datetime
from django.conf import settings
import stripe

from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

stripe.api_key=settings.STRIPE_SECRET_KEY

# Create your views here.
def home(request):
    return render(request,'common/home.html')

def form(request):
    if request.method == 'POST':       
        PROFILE=request.FILES.get('profile')
        FIRSTNAME=request.POST['FirstName']
        LASTNAME=request.POST['LastName']
        USERNAME=request.POST['username']
        EMAIL=request.POST['email']
        password=request.POST['password']
        ADDRESS=request.POST.get('address')
        CITY=request.POST['city']
        STATE=request.POST['state']
        PHONE=request.POST['phone']
        POSTAL_CODE=request.POST['postal_code']
        if User.objects.filter(username=USERNAME).exists():
            messages.error(request,'username already exist')
            return render(request,'common/form.html')
        if User.objects.filter(email=EMAIL).exists():
             messages.error(request,'email already exist')
             return render(request,'common/form.html')

        u=User.objects.create_user(first_name=FIRSTNAME,last_name=LASTNAME,username=USERNAME,password=password,email=EMAIL)
        u.save()
        customer=Register.objects.create(user=u,address=ADDRESS,phone=PHONE,postal_code=POSTAL_CODE,city=CITY,state=STATE,profile_photo=PROFILE)
        customer.save()
        customer_obj,create=Group.objects.get_or_create(name='CUSTOMER')
        customer_obj.user_set.add(u)
        messages.success(request,'Registration was successfull..')
        return redirect('login_user')
        
    return render(request,'common/form.html')


def login_user(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='CUSTOMER').exists():
            return redirect('userhome')
        else:
            return redirect('adminhome')
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            if user.groups.filter(name='CUSTOMER').exists():
                login(request,user)
                return redirect('userhome')
            else:
                return redirect('adminhome')
        else:
            messages.error(request,'Invalid username or password!')
            

    return render(request,'common/login.html')
    
        
@login_required

def userhome(request):
    data= Product.objects.all()
    category=request.GET.get('category')
    c=Category.objects.all()
    search=request.GET.get('search')
    if search:
        data=data.filter(Name__icontains=search)
    if category:
        data=data.filter(category_id=category)
    wishlistitems=wishlist.objects.filter(user=request.user).values_list('product_id',flat=True)
    return render(request, 'user/userhome.html', {'data':data,'c':c,'w':wishlistitems})

def productdetails(request, id):
    product = get_object_or_404(Product, id=id)
    r=review.objects.filter(product=product)
    return render(request, 'user/product_details.html', {'product': product,'r':r})

@login_required
def addtocart(request,id):
    product = get_object_or_404(Product,id=id)
    quantity = 1
    
    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))
        
    cart,created = Cart.objects.get_or_create(user=request.user)
    cart_item,created = Cartitems.objects.get_or_create(cart=cart,product=product,defaults={'quantity':quantity})
    

    if not created:
        new_quantity=cart_item.quantity+quantity
        if new_quantity<=product.stock:
            cart_item.quantity=new_quantity
        else:
            cart_item.quantity=product.stock
    cart_item.save()
    messages.success(request, f'{product.Name} added to cart.')
    return redirect('cartitems')

@login_required
def cartitems(request):
    cart = Cart.objects.get(user=request.user)
    items = Cartitems.objects.filter(cart=cart)

        
    grand_total = 0

    for item in items:
        item.total = item.product.Price * item.quantity
        grand_total += item.total
    
    

    return render(request,'user/cart.html',{'items':items,'grand_total': grand_total})
    


@login_required
def increasequantity(request,id):
    item=get_object_or_404(Cartitems,id=id)
    if item.quantity<item.product.stock:
        item.quantity+=1
        item.save()
    else:
        messages.error(request,'Out of Stock')
    return redirect('cartitems')


@login_required
def decreasequantity(request,id):
    item=get_object_or_404(Cartitems,id=id)
    if item.quantity<item.product.stock:
        item.quantity-=1
        item.save()
    if item.quantity == 0:
           item.delete()
    return redirect('cartitems')

@login_required
def removecart(request,id):
    item=get_object_or_404(Cartitems,id=id)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cartitems')

@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    items = Cartitems.objects.filter(cart=cart)

        
    grand_total = 0

    for item in items:
        item.total = item.product.Price * item.quantity
        grand_total += item.total
    
    

    return render(request,'user/checkout.html',{'items':items,'grand_total': grand_total})



@login_required
def cash_on_delivery(request):
    cart=Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('cartitems')
    cart_items=Cartitems.objects.filter(cart=cart)
    total=0
    for item in cart_items:
        total += item.product.Price*item.quantity
    order=Order.objects.create(
        user=request.user,
        orderdate=datetime.datetime.now(),
        paymentstatus='Pending',
        payment_method='COD',
        total_amount=total
        
    )
    for item in cart_items:
        orderitem.objects.create(
            order=order,
            product=item.product,
            price=item.product.Price,
            quantity=item.quantity
        )
        item.product.stock -= item.quantity
        item.product.save()
    cart_items.delete()
    return redirect('ordersuccess',order.id)


def ordersuccess(request,id):
    o=get_object_or_404(Order,id=id)
    return render(request,'user/ordersuccess.html',{'order':o})

@login_required
def vieworder(request):
    orders = orderitem.objects.filter(order__user=request.user)
    
    grand_total = 0

    for item in orders:
        item.total = item.product.Price * item.quantity
        grand_total += item.total
    return render(request,'user/vieworder.html',{'orders':orders,'grand_total': grand_total})

@login_required
def orderdetails(request,id):
    order = Order.objects.get(id=id)
    items = orderitem.objects.filter(order=order)

    return render(request,'user/orderdetails.html',{'order':order,'items':items}) 

@login_required
def userdetails(request):
    user_details=Register.objects.get(user=request.user)
    return render(request,'user/userdetails.html',{'user_details':user_details})

@login_required
def edituser(request):
    user_details= Register.objects.get(user=request.user)
    if request.method == "POST":
        if request.FILES.get('profile_photo'):
            user_details.profile_photo = request.FILES.get('profile_photo')
        user_details.user.first_name = request.POST['first_name']
        user_details.user.last_name = request.POST.get('last_name')
        user_details.user.username=request.POST.get('username')
        user_details.user.email = request.POST.get('email')
        user_details.phone = request.POST.get('phone')
        user_details.address = request.POST.get('address')
        user_details.city = request.POST.get('city')
        user_details.state = request.POST.get('state')
        user_details.postal_code = request.POST.get('postal_code')
        user_details.save()
        user_details.user.save()
        return redirect('userdetails')
    return render(request,'user/edituser.html',{'user_details':user_details})
    
        
@login_required
def upi(request):
    cart=Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('cartitems')
    cart_items=Cartitems.objects.filter(cart=cart)
    if not cart_items.exists():
        return redirect('cartitems')
    line_items=[]
    for item in cart_items:
            line_items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': item.product.Name,
                },
                'unit_amount': int(item.product.Price * 100),
            },
            'quantity': item.quantity,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://127.0.0.1:8000/payment_success',   
        cancel_url='http://127.0.0.1:8000/cartitems',
    )

    return redirect(session.url)
 
def payment_success(request):
    cart=Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('cartitems')
    cart_items=Cartitems.objects.filter(cart=cart)
    if not cart_items.exists():
        return redirect('cartitems')
    total=0
    for item in cart_items:
        total += item.product.Price*item.quantity
    order=Order.objects.create(
        user=request.user,
        orderdate=datetime.datetime.now(),
        paymentstatus='Paid',
        payment_method='UPI',
        total_amount=total,
        
        
    )
    for item in cart_items:
        orderitem.objects.create(
            order=order,
            product=item.product,
            price=item.product.Price,
            quantity=item.quantity
        )
        item.product.stock -= item.quantity
        item.product.save()
    cart_items.delete()
    return redirect('ordersuccess',order.id)

def generate_token():
     return get_random_string(20)

def password_reset_request(request):
    if request.method == "POST":
         email = request.POST.get('email')
         try:
             user = User.objects.get(email=email)
         except User.DoesNotExist:
             messages.error(request, "User with this email does not exist.")
             return redirect('password_reset_request')

         token =default_token_generator.make_token(user)
         uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
         reset_url = request.build_absolute_uri(reverse('password_reset_confirm',kwargs={'uidb64':uidb64,'token':token}))
         subject = "Password Reset Request"
         message = render_to_string('common/password_reset_email.html', {
             'user': user,
             'reset_url': reset_url,
         })
         send_mail(subject, message,settings.DEFAULT_FROM_EMAIL, [user.email])
         messages.success(request, "A password reset link has been sent to your email.")
         return render(request,'common/password_reset_email.html',{'user':user})
    return render(request,'common/password_reset_form.html')

def password_reset_confirm(request, uidb64, token):
        User=get_user_model()
        try:
          uid = force_str(urlsafe_base64_decode(uidb64))
          user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            print(user)
        if user is not None and default_token_generator.check_token(user,token):
             if request.method == 'POST':
                  password1=request.POST.get('password1')
                  password2=request.POST.get('password2')

                  if password1 == password2:
                      user.password = make_password(password1)
                      user.save()
                      messages.success(request,'your password has been reset')
                      return redirect('login_user')
                  else:
                      messages.error(request,'password do not match')
                      return render(request,'common/password_reset_form.html',{
            'uidb64': uidb64,
            'token': token
        })
                      
        return render(request, 'common/password_reset_confirm.html', {
            'uidb64': uidb64,
            'token': token
        })



def logout(request):
        if request.user.is_authenticated:
            request.session.flush()
        return redirect('home')



def add_to_wishlist(request,id):
    product=Product.objects.get(id=id)
    
    wishlist_item=wishlist.objects.filter(user=request.user,product=product).first()
    
    if wishlist_item:
        wishlist_item.delete()
    else:
        wishlist.objects.create(
            user=request.user,
            product=product
        )
    return redirect('userhome')


@login_required
def wishlistview(request):
    wishlist_items = wishlist.objects.filter(user=request.user).select_related('product')
    return render(request,'user/wishlist.html',{'wishlist_items':wishlist_items})




@login_required
def add_review(request,id):
    if request.method == 'POST':
        comment=request.POST.get('comment')
        rating=request.POST.get('rating')
        product=Product.objects.get(id=id)
        
        review.objects.create(
            user=request.user,
            product=product,
            comment=comment,
            rating=rating
            
        )
    return redirect('productdetails',id)