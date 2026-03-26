from django.db import models

# Create your models here.

# Category
# name description
class Category(models.Model):
    Name=models.CharField(max_length=100,null=True)
    Description=models.CharField(max_length=100,null=True)
    def __str__(self):
        return self.Name
    
class Product(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    Name=models.CharField(max_length=100,null=True)
    Price=models.FloatField(max_length=50,null=True)
    stock=models.IntegerField(null=True)
    image = models.ImageField(upload_to='products/',null=True)
    Description=models.TextField()
    
    

