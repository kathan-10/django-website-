from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('',views.home,name='home'),
    path('register/',views.register,name='register'),
    path('login/',views.Login,name='login'),
    path('cart/',views.cart,name='cart'),
    path('cartDisplay/',views.cartDisplay,name='cartDisplay'),
    path('logout/', views.logout_view, name='logout'),
    path('registerDetails/',views.registerDetails,name='registerDetails'),
    path('loginDetails/',views.loginDetails,name='loginDetails'),
    path('member/', views.member, name='member'),
    path('chackOut/',views.chackOut,name='chackOut'),
    path('shop/',views.shop,name='shop'),
    path('shopSearch/<str:query>/',views.shopSearch,name='shopSearch'),
    path('deleteItem/',views.deleteItem,name='deleteItem'),
    path('orderDetails/',views.orderDetails,name='orderDetails'),
    path('payment_success/',views.payment_success,name='payment_success'),
    path('payment_cancel/', views.payment_cancel, name='payment_cancel'),
    path('orderconfirm/',views.orderconfirm,name='orderconfirm'),
    path('clear_cart_and_home/',views.clear_cart_and_home,name='clear_cart_and_home'),
    path('adminWeb/',views.adminWeb,name='adminWeb'),
    path('delete_user/<str:id>/',views.delete_user,name='delete_user'),
    path('view_product/',views.view_product,name='view_product'),
    path('delete_product/<str:id>/',views.delete_product,name='delete_product'),
    path('add_product/',views.add_product,name='add_product'),
    path('addProduct_details/',views.addProduct_details,name='addProduct_details'),
    path('update_product/<str:id>/',views.update_product,name='update_product'),
    path('updateProduct_details/<str:id>/',views.updateProduct_details,name='updateProduct_details'),
    path('coupon/',views.coupon,name='coupon'),
    path('invoice/<int:order_id>/',views.download_invoice,name='invoice'),
    path('update_quantity/<int:cart_id>/',views.update_quantity,name='update_quantity'),
    path('charts',views.charts,name='charts'),
    path('forgot_password',views.forgot_password,name='forgot_password'),
    path('resetpassword',views.resetpassword,name='resetpassword'),
    path('verifyotp',views.verifyotp,name='verifyotp'),
    path('updatepassword',views.updatepassword,name='updatepassword')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)