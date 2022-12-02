from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from .utils import save_photo


#view the menu table
def view_menu(request):
    if request.session.has_key('admin_name'):
        cursor = connection.cursor()
        sql = "SELECT FOOD_ID, NAME, PRICE, DESCRIPTION, PICTURE FROM FOOD ORDER BY FOOD_ID"
        cursor.execute(sql)
        result = cursor.fetchall()
        connection.close()
        dict = []

        for r in result:
            food_id = r[0]
            item_name = r[1]
            price = r[2]
            description = r[3]
            picture = r[4]
            row = {'id':food_id, 'name':item_name, 'price':price, 'desc':description, 'pic':picture}
            dict.append(row)

        return render(request, "menu/menu_table.html", context={'dict':dict})
    return redirect('not_lgin_view')


# add new items to menu table in database
def add_menu_item(request):
    if request.session.has_key('admin_name'):
        if request.method == "POST":
            cursor = connection.cursor()
            sql = 'SELECT MAX(FOOD_ID) FROM FOOD'
            cursor.execute(sql)
            food_id = cursor.fetchone()
            food_id = food_id[0]
            if food_id is not  None:
                food_id = food_id + 1
            else:
                food_id = 1
            connection.close()

            print(str(request))

            item_name = request.POST.get("item_name")
            price = request.POST.get("price")
            desc = request.POST.get("description")
            photo = request.FILES.get('menu')
            photo = save_photo(photo, str(food_id)+"_"+item_name)

            cursor = connection.cursor()
            sql = "INSERT INTO FOOD VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, [food_id, item_name, price, desc, photo])
            connection.close()

            return redirect('view_menu')
        return render(request, "menu/add_item_form.html")
    return redirect('not_lgin_view')



#if request.session.has_key('admin_name'):
#return redirect('not_lgin_view')
