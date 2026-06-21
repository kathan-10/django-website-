from django.contrib import admin
from .models import Products,Cart,OrderConfirm,Coupon
@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','pname','pdesc','pprice','pstock','pimg')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id','uid','pid','quantity')

@admin.register(OrderConfirm)
class OrderConfirmAdmin(admin.ModelAdmin):
    list_display = ('id','uid','fname','lname','address','city','zipCode','mobile','email','shipDifferentAddress','orderNotes','payment_method','total','quantity','created_at')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('id','code','discount','valid_from','valid_to')

# Register your models here.
