from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from .utils import generate_primary_key
# Create your views here.

def place_order(request):
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

        cursor = connection.cursor()
        sql = "SELECT NAME FROM EMPLOYEES WHERE JOB_ID = (SELECT JOB_ID FROM JOB_TYPE WHERE UPPER(JOB_NAME) = 'WAITER')"
        cursor.execute(sql)
        result = cursor.fetchall()
        connection.close()
        dict2 = []
        for r in result:
            name = r[0]
            row = {'name':name}
            dict2.append(row)

        if request.method == "POST":
            cursor = connection.cursor()
            sql = "SELECT OFF_ORDER_ID.NEXTVAL FROM dual"
            cursor.execute(sql)
            order_id = cursor.fetchone()[0]
            order_id = 'OFF_' + str(order_id)

            sql = "SELECT MAX(FOOD_ID) FROM FOOD"
            cursor.execute(sql)
            total_item = cursor.fetchone()[0]

            ordered_items = []

            cursor = connection.cursor()
            sql = 'SELECT MAX(ITEM_ID) FROM ORDERED_ITEMS'
            cursor.execute(sql)
            item_id = cursor.fetchone()
            item_id = item_id[0]
            item_id = generate_primary_key(item_id)

            for i in range(1, total_item+1):
                if int(request.POST.get(str(i))) > 0:

                    cursor = connection.cursor()
                    sql = 'SELECT NAME FROM FOOD WHERE FOOD_ID = %s'
                    cursor.execute(sql, [i])
                    food_name = cursor.fetchone()[0]

                    row = {'item_id':item_id, 'order_id':order_id, 'food_id':i, 'food_name':food_name, 'quantity':int(request.POST.get(str(i)))}
                    ordered_items.append(row)
                    item_id = item_id + 1


            table_no = request.POST.get('table')
            man_name = request.session.get('admin_name')
            emp_name = request.POST.get('waiter')

            order_data = {'order_id':order_id, 'table_no':table_no, 'man_name':man_name, 'emp_name':emp_name}

            request.session['order_list'] = ordered_items
            request.session['order_data'] = order_data

            return redirect('confirm_order')

        return render(request, "admin_order/order_page.html", context={'dict':dict, 'dict2':dict2})
    return redirect('not_lgin_view')


def confirm_order(request):
    if request.session.has_key('admin_name'):
        if request.session.has_key('order_list'):
            ordered_items = request.session.get('order_list')
            order_data = request.session.get('order_data')

            if request.method == "POST":
                for row in ordered_items:
                    item_id = row.get('item_id')
                    order_id = row.get('order_id')
                    food_id = row.get('food_id')
                    quantity = row.get('quantity')
                    cursor = connection.cursor()
                    sql = "INSERT INTO ORDERED_ITEMS VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, [item_id, order_id, food_id, quantity])

                order_id = order_data.get('order_id')
                table_no = order_data.get('table_no')
                man_name = order_data.get('man_name')
                emp_name = order_data.get('emp_name')

                cursor = connection.cursor()
                cursor.callproc('INSERT_OFF_ORDER', [order_id, table_no, man_name, emp_name])

                request.session.pop('order_list')
                request.session.pop('order_data')

                return redirect('place_order')
            return render(request, "admin_order/confirm_order.html", context={'ordered_items':ordered_items, 'order_data':order_data})
        return redirect('place_order')
    return redirect('not_lgin_view')
