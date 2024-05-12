import json
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import *
from .utils import *
from django.conf import settings
from operator import itemgetter
import concurrent.futures as cf

# NOTE:
# + locals() là một hàm trong Python, nó trả về một dictionary chứa tất cả các biến cục bộ hiện có


# Create your views here.
def home(request):
    '''
    Hàm home: trang chủ của website
    '''
    return render(request, "home.html", locals())

def about(request):
    '''
    Hàm about: trang giới thiệu của website
    '''
    return render(request, "about.html", locals())

def contact(request):
    '''
    Hàm contact: trang liên hệ của website
    '''
    return render(request, "contact.html", locals())

def register(request):
    '''
    Hàm register: trang đăng ký tài khoản
    '''
    if request.method == "POST":
        re = request.POST
        rf = request.FILES

        # Kiểm tra xem email đã tồn tại hay chưa
        if User.objects.filter(username=re['username']).exists():
            messages.error(
                request, f"Email '{re['username']}' đã tồn tại. Vui lòng nhập email khác.")
            return render(request, "signup.html", locals())

        # Kiểm tra rỗng các trường thông tin
        try:
            if not re['username'] or not re['first_name'] or not re['last_name'] or not re['password'] or not re['address'] or not re['mobile'] or not rf['image']:
                messages.error(request, "Vui lòng điền đầy đủ thông tin")
                return render(request, "signup.html", locals())
        except:
            messages.error(request, "Vui lòng điền đầy đủ thông tin")
            return render(request, "signup.html", locals())

        # Nếu email chưa tồn tại, tạo user và register
        user = User.objects.create_user(
            username=re['username'], first_name=re['first_name'], last_name=re['last_name'], password=re['password'])
        register = Register.objects.create(
            user=user, address=re['address'], mobile=re['mobile'], image=rf['image'])
        messages.success(request, "Registration Successful")
        return redirect('signin')
    return render(request, "signup.html", locals())

def update_profile(request):
    if request.method == "POST":
        re = request.POST
        rf = request.FILES
        try:
            image = rf['image']
            data = Register.objects.get(user=request.user)
            data.image = image
            data.save()
        except:
            pass
        user = User.objects.filter(id=request.user.id).update(
            username=re['username'], first_name=re['first_name'], last_name=re['last_name'])
        register = Register.objects.filter(user=request.user).update(
            address=re['address'], mobile=re['mobile'])
        messages.success(request, "Updation Successful")
        return redirect('update_profile')
    return render(request, "update_profile.html", locals())

def signin(request):
    if request.method == "POST":
        re = request.POST
        user = authenticate(username=re['username'], password=re['password'])
        if user:
            login(request, user)
            messages.success(request, "Logged in successful")
            return redirect('home')
        else:
            messages.error(
                request, "Thông tin không hợp lệ. Vui lòng thử lại.")

    return render(request, "signin.html", locals())

def admin_signin(request):
    if request.method == "POST":
        re = request.POST
        user = authenticate(username=re['username'], password=re['password'])
        if user.is_staff:
            login(request, user)
            messages.success(request, "Logged in successful")
            return redirect('home')
    return render(request, "admin_signin.html", locals())

def change_password(request):
    if request.method == "POST":
        re = request.POST
        user = authenticate(username=request.user.username,
                            password=re['old-password'])
        if user:
            if re['new-password'] == re['confirm-password']:
                user.set_password(re['confirm-password'])
                user.save()
                messages.success(request, "Password changed successfully")
                return redirect('home')
            else:
                messages.success(request, "Password mismatch")
        else:
            messages.success(request, "Wrong password")
    return render(request, "change_password.html", locals())

def logout_user(request):
    logout(request)
    messages.success(request, "Logout Successfully")
    return redirect('home')

def search_product(request):
    product = []
    dictobj = {'object': []}
    if request.method == "POST":
        re = request.POST
        name = re['search']
        
        with cf.ThreadPoolExecutor(max_workers=4) as t_executor:
            chotot_thread = t_executor.submit(chotot, name)
            dienmayxanh_thread = t_executor.submit(dienmayxanh, name)   
            sendo_thread = t_executor.submit(sendo, name)
            dienmaycholon_thread = t_executor.submit(dienmaycholon, name)
            amazon_thread = t_executor.submit(amazon, name)
            
            chotot_price, chotot_name, chotot_image, chotot_link = chotot_thread.result()
            dienmayxanh_price, dienmayxanh_name, dienmayxanh_image, dienmayxanh_link = dienmayxanh_thread.result()
            sendo_price, sendo_name, sendo_image, sendo_link = sendo_thread.result()
            dienmaycholon_price, dienmaycholon_name, dienmaycholon_image, dienmaycholon_link = dienmaycholon_thread.result()
            amazon_price, amazon_name, amazon_image, amazon_link = amazon_thread.result()
        
        # *********************Crawl data từ Chợ Tốt******************************************  
        
                 # Xử lý dữ liệu Chợ Tốt
        dictobj["object"].append({'logo': '/static/assets/' + 'img/' + 'chotot-logo.png',       
                                    'price': convert(chotot_price),
                                    'name': chotot_name,
                                    'link': chotot_link,
                                    'image': chotot_image
                                    })

        # *************************************************************************************
        
        # ========================================================================================

        # ===================================Điện máy xanh=======================================
        # dienmayxanh_price, dienmayxanh_name, dienmayxanh_image, dienmayxanh_link = dienmayxanh(name)
        dictobj["object"].append({'logo': '/static/assets/' + 'img/' + 'dienmayxanh-logo.png',
                                  'price': convert(dienmayxanh_price),
                                  'name': dienmayxanh_name,
                                  'link': dienmayxanh_link,
                                  'image': dienmayxanh_image
                                  })
        # ========================================================================================

        # ===================================Sendo=================================================
        # sendo_price, sendo_name, sendo_image, sendo_link = sendo(name)
        dictobj["object"].append({'logo': '/static/assets/' + 'img/' + 'sendo-logo.png',
                                  'price': convert(sendo_price),
                                  'name': sendo_name,
                                  'link': sendo_link,
                                  'image': sendo_image
                                  })
        # =========================================================================================

        # ===================================Điện máy chợ lớn=============================================
        # dienmaycholon_price, dienmaycholon_name, dienmaycholon_image, dienmaycholon_link = dienmaycholon(name)
        dictobj["object"].append({'logo': '/static/assets/' + 'img/' + 'dienmaycholon-logo.png',
                                  'price': convert(dienmaycholon_price),
                                  'name': dienmaycholon_name,
                                  'link': dienmaycholon_link,
                                  'image': dienmaycholon_image
                                  })
        # ===============================================================================================

        # ===================================Amazon=================================================
        # amazon_price, amazon_name, amazon_image, amazon_link=amazon(name)
        dictobj["object"].append({'logo':'/static/assets/' + 'img/' + 'amazon-logo.png',
                                  'price':convert(amazon_price)*305,
                                  'name':amazon_name,
                                  'link':amazon_link,
                                  'image':amazon_image
                                  })
        # ========================================================================================

        data = dictobj['object']
        # Nếu giá trị nào bằng 0 thì xóa nó
        data = [i for i in data if i['price'] != '0']
    
        data = sorted(data, key=itemgetter('price'))
        check_flag = False

        # Chuyển đổi tiền tệ từ sang VND
        for i in range(len(data)):
            if not check_flag:
                check_flag = (data[i]['name'] != '0') and (not check_flag)
                
                data[i]['check_flag'] = check_flag
            else:
                data[i]['check_flag'] = not check_flag
                
            data[i]['price'] = format_price(data[i]['price'])

        dictobj['object'] = data

        history = History.objects.create(user=request.user, product=dictobj)
        # messages.success(request, "History Saved")

    return render(request, "search_product.html", locals())


def my_history(request):
    history = History.objects.filter(user=request.user).order_by('-created')

    # Check if the current user is a staff member
    if request.user.is_staff:
        # If the user is staff, retrieve all history objects (override previous filter)
        history = History.objects.all()
    
    # Adjust timestamps to milliseconds
    for i in history:
        i.created = i.created.timestamp() * 1000
        
    # Render the template 'my_history.html' with the 'history' variable available
    return render(request, "my_history.html", locals())



def all_user(request):
    data = Register.objects.filter()
    return render(request, "all_user.html", locals())

# Hàm xem chi tiết lịch sử tìm kiếm
def history_detail(request, pid):
    history = History.objects.get(id=pid)
    # print(history.product)
    # product = (history.product).replace("'", '"')
    # product = json.loads(str(product))
    product = eval(history.product)['object']
    product = sorted(product, key=itemgetter('price'))
    try:
        user = Register.objects.get(user=history.user)
    except:
        pass
    return render(request, "history_detail.html", locals())

# Hàm xóa user của admin
def delete_user(request, pid):
    user = User.objects.get(id=pid)
    user.delete()
    messages.success(request, "User Deleted")
    return redirect('all_user')

# Hàm xóa lịch sử tìm kiếm
def delete_history(request, pid):
    data = History.objects.get(id=pid)
    data.delete()
    messages.success(request, "History Deleted")
    return redirect('my_history')
