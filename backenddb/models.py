from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
class Products(models.Model):
        pname = models.CharField(max_length=20)
        pdesc = models.CharField(max_length=20)
        pprice = models.CharField(max_length=20)
        pstock = models.CharField(max_length=20,null=True)
        pimg = models.ImageField(upload_to="product_img/",null=True,blank=True)

class Cart(models.Model):
        uid = models.ForeignKey(User,on_delete=models.CASCADE)
        pid = models.ForeignKey(Products,on_delete=models.CASCADE)
        quantity = models.CharField(max_length=10,null=True,default=1)

class Coupon(models.Model):
        code = models.CharField(max_length=50, unique=True)
        discount = models.DecimalField(max_digits=5,decimal_places=2)
        valid_from = models.DateTimeField()
        valid_to = models.DateTimeField()
        user_used = models.ManyToManyField(User,blank=True)

        def is_active(self):
                now = timezone.now()
                return self.valid_from <= now <= self.valid_to
        def __str__(self):
                return self.code
class OrderConfirm(models.Model):
        uid = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
        fname = models.CharField(max_length=20)
        lname = models.CharField(max_length=20)
        address = models.CharField(max_length=20)
        city = models.CharField(max_length=20)
        zipCode = models.CharField(max_length=20)
        mobile = models.CharField(max_length=20)
        email = models.EmailField(max_length=20)
        shipDifferentAddress = models.CharField(max_length=20)
        orderNotes = models.CharField(max_length=20)
        payment_method = models.CharField(null=True,max_length=10)
        total = models.CharField(null=True,max_length=10)
        quantity = models.CharField(null=True,max_length=10)
        created_at = models.DateField(null=True,auto_now_add=True)

def __str__(self):
        return self.title
# Create your models here.
