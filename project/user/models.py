from django.db import models
from django.contrib.auth.models import User
from manager.models import Product

# Create your models here.


class Register(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=10)
    address=models.TextField()
    postal_code=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    profile_photo=models.FileField(upload_to='profile')
    
    
    
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    
    
class Cartitems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
        
    
class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    orderdate=models.CharField(max_length=100)
    deliverydate=models.CharField(max_length=100)
    orderstatus=models.CharField(max_length=100,default='pending')
    paymentstatus=models.CharField(max_length=100)
    payment_method=models.CharField(max_length=100)
    tracking_id=models.CharField(max_length=100)
    carrier=models.CharField(max_length=100)
    total_amount=models.IntegerField(null=True)


class orderitem(models.Model):
   order = models.ForeignKey(Order, on_delete=models.CASCADE)
   product = models.ForeignKey(Product, on_delete=models.CASCADE)
   price=models.IntegerField(null=True)
   quantity=models.IntegerField(default=1)
    
# wishlist
# review


# user,product
class wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)



# Review
# user,product,comment,rating,created_at
class review(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment=models.TextField(max_length=100)
    rating=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
        