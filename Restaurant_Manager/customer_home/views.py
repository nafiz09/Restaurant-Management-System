from django.shortcuts import render, redirect

# Create your views here.
def customer_home(request):
    if request.session.has_key('customer_name'):
        return render(request, "customer_login/home_login.html")
    return redirect('nt_lg_in')


def logout(request):
    if request.session.has_key('customer_name'):
        request.session.pop('customer_name')
        return redirect("home")
    return render(request, 'customer_login/signup.html')
