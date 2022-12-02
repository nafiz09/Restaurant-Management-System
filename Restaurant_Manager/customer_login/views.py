from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password


# Create your views here.
def home(request):
    if request.session.has_key('customer_name'):
        return render(request, "customer_login/home_login.html")
    return render(request,'customer_login/home.html')

def login(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        cursor = connection.cursor()
        sql = "SELECT PASSWORD FROM CUSTOMERS WHERE NAME = %s"
        cursor.execute(sql, [name])
        result = cursor.fetchone()
        connection.close()

        if result and check_password(password, result[0]):
            request.session['customer_name'] = name
            return redirect('cus_home')
        else:
            return render(request, "customer_login/login.html", context = {'status':'Log in failed'})


    return render(request, "customer_login/login.html")


def signup(request):
        if request.method == "POST":
            name = request.POST.get('name')
            mail = request.POST.get('mail')
            password = make_password( request.POST.get('pass') )
            address = request.POST.get('address')
            phone = request.POST.get('phone')

            cursor = connection.cursor()
            sql = 'SELECT MAX(CUSTOMER_ID) FROM CUSTOMERS'
            cursor.execute(sql)
            last_id = cursor.fetchone()
            last_id = last_id[0]
            if last_id is not  None:
                user_id = last_id + 1
            else:
                user_id = 1

            cursor = connection.cursor()
            sql = "INSERT INTO CUSTOMERS VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, [user_id, name, mail, phone, address, password])

            return redirect('login')

        return render(request, 'customer_login/signup.html')


def not_lgin(request):
    return render(request, "customer_login/ntlgin.html")
