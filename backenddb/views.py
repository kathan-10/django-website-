from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import Products,Cart,OrderConfirm,Coupon
from decimal import Decimal
from email.message import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Cast
from django.db.models import Count,FloatField, Sum
from datetime import date
import paypalrestsdk,smtplib,matplotlib,random
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import io,base64


EMAIL_ADDRESS='example@gmail.com'
EMAIL_PASSWORD='examplepassword'
from django.contrib.auth.decorators import login_required
def home(request):
    if request.user.is_authenticated:
        return render(request,"user/member.html",{"username":request.user.username})
    else:
        productDetails = Products.objects.all()
        return render(request,"user/index.html",{'productDetails':productDetails})

def forgot_password(request):
        return render(request,"user/forgotpassword.html")

def resetpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user_obj = User.objects.filter(email=email)
        if user_obj:
            otp = str(random.randint(10000, 999999))
            request.session['otp'] = otp
            request.session['email'] = email
            msg=EmailMessage()
            msg['subject']='OTP Verification'
            msg['from']=EMAIL_ADDRESS
            msg['to']=email
            msg_text=(
                f"Your OTP Is {otp}."
            )
            msg.set_content(msg_text)
            with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
                messages.success(request, "OTP has been sent to your email address.")
                return render(request,"user/otpcheck.html")
        else:
            return HttpResponse("No User Found")

def verifyotp(request):
    email=request.session.get('email')
    if not email:
        return redirect("home")
    else:
        if request.method=='POST':
            otp=request.POST.get('otp')
            otp1=request.session.get('otp')
            if otp==otp1:
                return render(request,"user/passwordreset.html")
            else:
                return HttpResponse("Invaild Otp")

def updatepassword(request):
    email = request.session.get('email')
    if not email:
        return redirect("home")
    else:
        if request.method=='POST':
            newPassword=request.POST.get('new_password')
            try:
                if newPassword:
                    user_obj = User.objects.filter(email=email)
                    user_obj.set_password(newPassword)
                    user_obj.save()
                    del request.session['otp']
                    del request.session['email']
                    return redirect("login")
                else:
                    return HttpResponse("Password Is Not Found")
            except Exception as e:
                return HttpResponse(e)

@login_required
def member(request):
        productDetails = Products.objects.all()
        pcount = Cart.objects.filter(uid_id=request.user.id).count()
        return render(request,"user/member.html",{"username":request.user.username,'productDetails':productDetails,"uid":request.user.id,"pcount":pcount})
def register(request):
    return render(request,"user/register.html")

def registerDetails(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('confirm')

        if password == cpassword:
            if User.objects.filter(email=email).exists():
                return HttpResponse("User Already Exists")
            user = User.objects.create_user(username=username,email=email,password=password)
            user.save()
            return redirect("login")
        return HttpResponse("Password And Confirm Password Does Not Match")

def loginDetails(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(email=email).first()
        if not user_obj:
            return HttpResponse("User Not Found")

        user = authenticate(request,username=user_obj.username,password=password)
        if not user:
            return HttpResponse("Wrong Email Or Password")

        login(request, user)
        if user.email == 'admin12@gmail.com':
                return redirect("adminWeb")

        return redirect("member")

@login_required
def deleteItem(request):
        if request.method == 'POST':
            id = request.POST.get('id')
            cdelete = Cart.objects.filter(id=id)
            cdelete.delete()
        return redirect("cartDisplay")

@login_required
def cartDisplay(request):
        pcount = Cart.objects.filter(uid_id=request.user.id).count()
        cart_items = Cart.objects.filter(uid_id=request.user.id)
        coupon_id = request.session.get('coupon_id')
        subtotal = Decimal('0.00')
        total = Decimal('0.00')

        for item in cart_items:
            item.item_total = Decimal(str(item.pid.pprice)) * Decimal(item.quantity)
            subtotal+=item.item_total
        request.session['subtotal'] = str(subtotal)


        #check condition if less then total and coupon active beacuse of session then not applied
        if subtotal < Decimal('100') and request.session.get('coupon_id'):
            try:
                del request.session['coupon_id']
                messages.info(request, "Coupon removed because subtotal dropped below Rs 100")
            except KeyError:
                pass

        #check coupon is ?
        coupon = None
        if coupon_id:
            coupon = Coupon.objects.get(id=coupon_id)

        #subtotal less then 100 charges
        if subtotal >= 100:
            shipping = Decimal('0.00')
        else:
            shipping = Decimal('50.00')

        #condition if subtotal greater than 100 and coupon then applied
        if subtotal>=100 and coupon and coupon.is_active():
                discount_amount = (subtotal * Decimal(coupon.discount)) / Decimal(100)
        else:
                discount_amount = Decimal('0.00')

        total = round(subtotal + shipping - discount_amount,2)
        return render(request, "user/cart.html",{"username": request.user.username, "cart_items": cart_items, "subtotal": subtotal,"total": total, "pcount": pcount,"discount": coupon.discount if coupon else 0})


@login_required
def shop(request):
        psearch = Products.objects.filter(pname="Apple")
        pcount = Cart.objects.filter(uid_id=request.user.id).count()
        return render(request,"user/shop.html",{"product":psearch,"username":request.user.username,"pcount":pcount})

@login_required
def shopSearch(request,query):
            psearch = Products.objects.filter(pname=query)
            pcount = Cart.objects.filter(uid_id=request.user.id).count()
            return render(request,"user/shop.html",{"product":psearch,"uid":request.user.id,"pcount":pcount})

@login_required
def cart(request):
      if request.method == 'POST':
          pid = request.POST.get('pid')
          product = Products.objects.get(id=pid)
          cart = Cart(uid=request.user,pid=product)
          cart.save()
          return redirect("cartDisplay")


@login_required
def chackOut(request):
        pcount = Cart.objects.filter(uid_id=request.user.id).count()
        cart_items = Cart.objects.filter(uid_id=request.user.id)
        coupon_id = request.session.get("coupon_id")
        subtotal = Decimal('0.00')
        total = Decimal('0.00')

        if pcount == 0:
            return HttpResponse("No Product Selected")


        for item in cart_items:
            item.item_total = Decimal(str(item.pid.pprice)) * Decimal(item.quantity)
            subtotal += item.item_total

        request.session['subtotal'] = str(subtotal)

        if subtotal < Decimal('100') and request.session.get('coupon_id'):
            try:
                del request.session['coupon_id']
                messages.info(request, "Coupon removed because subtotal dropped below Rs 100")
            except KeyError:
                pass
        coupon = None
        if coupon_id:
            coupon = Coupon.objects.get(id=coupon_id)

        if subtotal >= 100:
            shipping = Decimal('0.00')
        else:
            shipping = Decimal('50.00')

        if coupon and coupon.is_active():
                discount_amount = (subtotal * Decimal(coupon.discount)) / Decimal(100)
        else:
                discount_amount = Decimal('0.00')

        total = round(subtotal + shipping - discount_amount,2)

        return render(request,"user/chackout.html",{"username":request.user.username,"cart_items":cart_items,"subtotal":subtotal,"total":total,"pcount":pcount,"discount": coupon.discount if coupon else 0})

@login_required
def orderDetails(request):
        if request.method == 'POST':
            fname = request.POST.get('fname','').strip()
            lname = request.POST.get('lname','').strip()
            address = request.POST.get('address','').strip()
            city = request.POST.get('city','').strip()
            zipCode = request.POST.get('zipCode','').strip()
            mobile = request.POST.get('mobile','').strip()
            email = request.POST.get('email','').strip()
            shipDifferentAddress = request.POST.get('shipDifferentAddress')
            shipDifferentAddress = 'yes' if shipDifferentAddress == "yes" else "no"
            orderNotes = request.POST.get('orderNotes')
            COD = request.POST.get('COD')
            paypal = request.POST.get('PayPal')
            total = request.POST.get('total','').strip()
            quan = request.POST.get('quan')
            required_fields = [fname, lname, address, city, zipCode, mobile, email]

            if any(filed == '' for filed in required_fields):
                return HttpResponse("Error: All required fields must be filled.")


            if paypal:
                paypalrestsdk.configure({
                    "mode":"sandbox",
                    "client_id": "demo",
                    "client_secret": "demo"
                })
                payment = paypalrestsdk.Payment({
                        "intent":"sale",
                        "payer":{
                            "payment_method":"paypal"
                        },
                        "redirect_urls":{
                            "return_url": "http://localhost:8000/payment_success/",
                            "cancel_url": "http://localhost:8000/payment_cancel/"
                        },
                        "transactions":[{
                            "amount":{
                                "total":total,
                                "currency":"USD"
                            },
                            "description": "Purchase from Django Website"
                        }]
                })
                if payment.create():
                    for link in payment.links:
                        if link.rel == "approval_url":
                            approval_url = str(link.href)
                            cart = Cart.objects.filter(uid_id=request.user.id)
                            Order = OrderConfirm(uid=request.user,fname=fname,lname=lname,address=address,city=city,zipCode=zipCode,mobile=mobile,email=email,shipDifferentAddress=shipDifferentAddress,orderNotes=orderNotes,payment_method="PayPal",total=total,quantity=quan)
                            Order.save()
                            return redirect(approval_url)
                else:
                    return HttpResponse("Payment creation failed: " + str(payment.error))
            elif COD:
                    Order = OrderConfirm(uid=request.user,fname=fname, lname=lname, address=address,city=city, zipCode=zipCode, mobile=mobile, email=email,shipDifferentAddress=shipDifferentAddress, orderNotes=orderNotes,payment_method="COD",total=total,quantity=quan)
                    Order.save()
                    return redirect("orderconfirm")
            else:
                return HttpResponse("Please Select Payment Method")

@login_required
def orderconfirm(request):
    order = OrderConfirm.objects.filter(uid_id=request.user.id).order_by('-id').first()

    oid = order.id
    ouid = order.uid

    cart = Cart.objects.filter(uid_id=ouid).select_related('pid')

    for item in cart:
        product = item.pid
        pquan = item.quantity

        if int(product.pstock) >= int(pquan):
            product.pstock = int(product.pstock) - int(pquan)
            product.save()
        else:
            return HttpResponse("Out of Stock Product")

    oitems = [item.pid.pname for item in cart if item.pid is not None]
    oitems_str = ", ".join(oitems)
    ototal = order.total
    oquan = order.quantity


    oadd = order.address
    opayment_method = order.payment_method
    ocreated = order.created_at
    oemail = order.email
    msg =EmailMessage()
    msg['subject'] = 'Confirmation Of Your Order'
    msg['from'] = EMAIL_ADDRESS
    msg['to'] = oemail
    msg_text = (
        f'Your Order Is Placed\n'
        f'Order Id Is {oid}\n'
        f'Order Item Is {oitems_str}\n'
        f'Customer Address Is {oadd}\n'
        f'Total Amount Is {ototal}\n'
        f'Total Quantity Is {oquan}\n'
        f'Payment Method Is {opayment_method}\n'
        f'Order Created At {ocreated}\n'
        f'Thank You For Choosing Fruitable\n'
    )
    msg.set_content(msg_text)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
            smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        return HttpResponse(e)
    coupon_id = request.session.get("coupon_id")
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            coupon.user_used.add(request.user)
            coupon.save()
            del request.session["coupon_id"]
        except Coupon.DoesNotExist:
            pass
    return render(request, "user/orderconfirm.html", {"order": order,"order_items":oitems_str})

def clear_cart_and_home(request):
    Cart.objects.filter(uid_id=request.user.id).delete()
    return redirect("member")
@login_required
def payment_success(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if not payment_id and payer_id:
        return HttpResponse("Missing paymentId or PayerID.")

    paypalrestsdk.configure({
        "mode": "sandbox",
        "client_id": "demo",
        "client_secret": "demo"

    })
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id":payment.payer.payer_info.payer_id}):
        return redirect("orderconfirm")
    else:
        return HttpResponse("Payment execution failed: " + str(payment.error))

def payment_cancel(request):
    return redirect("chackOut")

def Login(request):
    return render(request,"user/login.html")

def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect("home")

def coupon(request):
    if request.method == 'POST':
        coupon = request.POST.get('coupon')
    try:
        coupon = Coupon.objects.get(code=coupon)
    except Coupon.DoesNotExist:
            messages.error(request,"Invaild Coupon")
            return redirect("cartDisplay")

    subtotal_str=request.session.get('subtotal')
    subtotal = Decimal(subtotal_str)
    if subtotal < Decimal(100):
        messages.error(request, "Coupon Can not applied if total is not above 100",extra_tags="coupon")
        return redirect("cartDisplay")
    if not coupon.is_active():
        messages.error(request, "Coupon expired or not yet active",extra_tags="coupon")
        return redirect("cartDisplay")
    if request.user in coupon.user_used.all():
        messages.error(request, "You already used this coupon",extra_tags="coupon")
        return redirect("cartDisplay")
    request.session['coupon_id'] = coupon.id
    messages.success(request, f"Coupon {coupon.code} applied successfully!",extra_tags="coupon")
    return redirect("cartDisplay")

@login_required
def download_invoice(request,order_id):
    try:
        order=OrderConfirm.objects.get(id=order_id,uid=request.user)
    except OrderConfirm.DoesNotExist:
        return HttpResponse("Order Not Found")

    cart_items=Cart.objects.filter(uid_id=request.user.id).select_related('pid')
    item_list=[item.pid.pname for item in cart_items if item.pid]

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{order.id}.pdf"'

    p=canvas.Canvas(response,pagesize=letter)
    width,height = letter

    p.setFont("Helvetica-Bold", 18)
    p.drawString(200, 750, "Fruitable - Invoice")

    p.setFont("Helvetica", 12)
    p.drawString(30, 720, f"Order ID: {order.id}")
    p.drawString(30, 700, f"Customer: {order.fname} {order.lname}")
    p.drawString(30, 680, f"Email: {order.email}")
    p.drawString(30, 660, f"Address: {order.address}, {order.city}")
    p.drawString(30, 640, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(30, 620, f"Payment: {order.payment_method}")
    p.drawString(30, 600, f"Quantity: {order.quantity}")
    p.drawString(30, 580, f"Total Amount: Rs.{order.total}")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(30, 560, "Items:")
    p.setFont("Helvetica", 12)

    y = 540
    for item in item_list:
        p.drawString(40, y, f"- {item}")
        y -= 20

    p.showPage()
    p.save()
    return response

@csrf_exempt
def update_quantity(request,cart_id):
    if request.method == 'POST':
        quan=request.POST.get('quan')
        cart1 = Cart.objects.get(uid=request.user,id=cart_id)
        tstock = cart1.pid.pstock

        if int(tstock) < int(quan):
            messages.error(request, f"Only {tstock} items available",extra_tags="stock")
            return redirect("cartDisplay")

        if int(quan) < 1:
            quan=1
        cart = Cart.objects.get(id=cart_id)
        cart.quantity=quan
        cart.save()
        return redirect('cartDisplay')
# ---------------------------ADMIN---------------------------------------
@login_required
def adminWeb(request):
    username = request.user.username
    user = User.objects.exclude(is_superuser=True).exclude(username='adminfruitable')
    today = date.today()
    data = OrderConfirm.objects.values('created_at').annotate(order_count=Count('id'))

    labels = [row['created_at'].strftime('%d-%m-%Y') for row in data]
    values = [row['order_count'] for row in data]

    plt.figure(figsize=(5, 3))

    bars = plt.bar(labels, values, width=0.4)

    plt.title("Orders Received Per Day", fontsize=12)
    plt.ylabel("Number of Orders")
    plt.xlabel("Date")

    if values:
        max_value = max(values)
    else:
        max_value = 0

    plt.ylim(0, max(values) + 2)

    for bar in bars:
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(int(bar.get_height())),
            ha='center',
            va='bottom',
            fontsize=11
        )

    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    graph = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close()
    return render(request,"adminWeb/index.html",{"username":username,"user":user,'graph':graph})

def delete_user(request,id):
     User.objects.get(id=id).delete()
     return redirect("adminWeb")

@login_required
def view_product(request):
    username = request.user.username
    products = Products.objects.all()
    return render(request,"adminWeb/viewProducts.html",{"username":username,"products":products})

@login_required
def delete_product(request,id):
    Products.objects.get(id=id).delete()
    return redirect("view_product")

@login_required
def add_product(request):
    username = request.user.username
    return render(request,"adminWeb/addProduct.html",{'username':username})

@login_required
def update_product(request,id):
    product = Products.objects.get(id=id)
    username = request.user.username
    return render(request, "adminWeb/updateProduct.html", {'username': username,'product':product})


@login_required
def updateProduct_details(request,id):
    product = Products.objects.get(id=id)

    if product:
        if request.method == 'POST':
            pname = request.POST.get('pname')
            pdesc = request.POST.get('pdesc')
            pprice = request.POST.get('pprice')
            pstock = request.POST.get('pstock')
            pimg = request.FILES.get('pimg')

            if pname:
                product.pname = pname
            if pdesc:
                product.pdesc = pdesc
            if pprice:
                product.pprice = pprice
            if pstock:
                product.pstock = pstock
            if pimg:
                product.pimg = pimg
            product.save()
            return redirect("view_product")
    else:
        return HttpResponse("NO DATA FOUND")

@login_required
def addProduct_details(request):
    if request.method == 'POST':
        pname = request.POST.get('pname')
        pdesc = request.POST.get('pdesc')
        pprice = request.POST.get('pprice')
        pstock = request.POST.get('pstock')
        pimg = request.FILES.get('pimg')

        if all([pname,pdesc,pprice,pstock,pimg]):
            Product = Products(
                pname=pname,
                pdesc=pdesc,
                pprice=pprice,
                pstock=pstock,
                pimg=pimg
            )
            Product.save()
            return redirect("view_product")
        else:
            return HttpResponse("ALL FIELD ARE REQUIRED")


def orders_trend_chart():
    data = OrderConfirm.objects.values('created_at').annotate(order_count=Count('id'))
    dates = [d['created_at'].strftime('%d-%m') for d in data]
    counts = [d['order_count'] for d in data]

    plt.figure(figsize=(6, 3))
    plt.plot(dates, counts, marker='o')
    plt.title("Orders Trend")
    plt.xlabel("Date")
    plt.ylabel("Orders")
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph = base64.b64encode(buf.getvalue()).decode()
    plt.close()
    return graph


def payment_method_pie():
    data = OrderConfirm.objects.values('payment_method').annotate(order_count=Count('id'))
    labels = [d['payment_method'] or 'Unknown' for d in data]
    sizes = [d['order_count'] for d in data]

    plt.figure(figsize=(4,4))
    plt.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90)
    plt.title("Payment Methods")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph = base64.b64encode(buf.getvalue()).decode()
    plt.close()
    return graph

def revenue_per_day():
    data = (OrderConfirm.objects.annotate(total_num=Cast('total', FloatField())).values('created_at').annotate(revenue=Sum('total_num')).order_by('created_at'))

    dates = [d['created_at'].strftime('%d-%m') for d in data]
    revenue = [d['revenue'] or 0 for d in data]

    plt.figure(figsize=(6,3))
    plt.bar(dates, revenue, width=0.5)
    plt.title("Revenue per Day")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph = base64.b64encode(buf.getvalue()).decode()
    plt.close()
    return graph

@login_required
def charts(request):
    context = {
        'trend_graph': orders_trend_chart(),
        'payment_graph': payment_method_pie(),
        'revenue_graph': revenue_per_day(),
    }
    return render(request, "adminWeb/charts.html", context)
# Create your views here.
