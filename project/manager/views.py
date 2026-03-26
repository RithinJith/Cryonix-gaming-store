from django.shortcuts import render,redirect,get_object_or_404
from .models import Category,Product
from django.contrib import messages
from user.models import Order, orderitem, Register
import datetime

# Create your views here.
def adminhome(request):
    user_count = Register.objects.count()
    product_count = Product.objects.count()
    order_count = Order.objects.count()
    return render(request, 'manager/adminhome.html', {
        'user_count': user_count,
        'product_count': product_count,
        'order_count': order_count,
    })

def category(request):
    if request.method == 'POST':
        Name=request.POST['Name']
        Description=request.POST['Description']
        
        category=Category.objects.create(Name=Name,Description=Description)
        category.save()
            
        messages.success(request,'CATEGORY ADDED SUCCESSFULL')
    
    return render(request,'manager/category.html')



def view(request):
    v=Category.objects.all()
    return render(request,'manager/viewcate.html',{'data':v})


def delete(request,id):
    Category.objects.filter(id=id).delete()
    messages.success(request,'DELETED SUCCESSFULL')
    return redirect('view')
    
    
def editdata(request,id):
    e=get_object_or_404(Category,id=id)  
    if request.method == 'POST':
        e.Name=request.POST['Name']
        e.Description=request.POST['Description']
        e.save()
    r=Category.objects.filter(id=id)
    return render(request,'manager/edit.html',{'edata':r})


def add_product(request):
    c=Category.objects.all()   
    if request.method == 'POST':       
        IMAGE=request.FILES.get('image')
        NAME=request.POST['Name']
        PRICE=request.POST['price']
        STOCK=request.POST['stock']
        CATEGORY=request.POST['category']
        DESCRIPTION=request.POST.get('description')
        
        product=Product.objects.create(image=IMAGE,Name=NAME,Price=PRICE,stock=STOCK,category_id=CATEGORY,Description=DESCRIPTION)
        product.save()
    
    return render(request,'manager/product.html',{'c':c})


def view_prodct(request):
    viewproduct=Product.objects.all()
    return render(request,'manager/view_prodct.html',{'data':viewproduct})


def delete_prodct(request,id):
    Product.objects.filter(id=id).delete()
    messages.success(request,'DELETED SUCCESSFULL')
    return redirect('view_prodct')
    
    
def edit_prodct(request,id):
    c=Category.objects.all() 
    p=get_object_or_404(Product,id=id)  
    if request.method == 'POST':
        p.Name=request.POST['Name']
        p.Price=request.POST['price']
        p.stock=request.POST['stock']
        p.category_id=request.POST['category']
        if 'image' in request.FILES:
            p.image=request.FILES['image']
        p.save()
    editproduct=Product.objects.filter(id=id)
    
    return render(request,'manager/edit_prodct.html',{'pdata':editproduct,'c':c})

def cancel_order(request,id):
    order=get_object_or_404(Order,id=id)
    order.orderstatus='Canceled'
    order.paymentstatus='Failed'
    order.save()
    return redirect('userorder_for_admin')

def Completeorder(request,id):
    order=get_object_or_404(Order,id=id)
    order.orderstatus='Completed'
    order.paymentstatus='Paid'
    order.save()
    return redirect('userorder_for_admin')

def userorder_for_admin(request):
    status = request.GET.get('status')

    orders = orderitem.objects.select_related('product', 'order')

    if status == 'pending':
        orders = orders.filter(order__orderstatus='pending')

    elif status == 'Processing':
        orders = orders.filter(order__orderstatus='Processing')

    elif status == 'Completed':
        orders = orders.filter(order__orderstatus='Completed')

    elif status == 'Canceled':
        orders = orders.filter(order__orderstatus='Canceled')

    elif status == 'all':
        orders = orders

    return render(request, 'manager/userorder.html', {'order': orders})



def orderdetails_for_manager(request,id):
    order = get_object_or_404(Order,id=id)
    item = orderitem.objects.select_related('product').filter(order=order).first()
    user_details = Register.objects.filter(user=order.user).first()
    if request.method == "POST":

        if 'start_processing' in request.POST:
            order.orderstatus = 'Processing'
            order.paymentstatus = 'Pending'
            order.deliverydate = request.POST['delivery_Date']
            order.carrier = request.POST['carrier']
            order.tracking_id = request.POST['TrackingID']
            order.save()

        if 'cancel_order' in request.POST:
            order.orderstatus = 'Canceled'
            order.paymentstatus = 'Failed'
            order.save()

    return render(request,'manager/orderdetails.html',{
        'order':order,
        'item':item,
        'user_details':user_details
    })