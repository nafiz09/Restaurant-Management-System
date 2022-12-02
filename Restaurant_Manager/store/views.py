from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from .utils import generate_primary_key

# Create your views here.
def store(request):
    if request.session.has_key('customer_name'):
        search_str = ""
        selected_item = "dummy_str"
        name = request.session.get('customer_name')
        cursor = connection.cursor()
        sql = "SELECT CUSTOMER_ID FROM CUSTOMERS WHERE NAME = %s"
        cursor.execute(sql,[name])
        customer_id = cursor.fetchone()[0]
        connection.close()

        cursor = connection.cursor()
        sql = "SELECT CART_ID FROM CART WHERE CUSTOMER_ID = %s"
        cursor.execute(sql,[customer_id])
        cart_id = cursor.fetchone()[0]
        connection.close()

        if request.method == "POST":
            if request.POST.get('search_area'):
                search_str = request.POST.get('search_area')
            if request.POST.get('selected'):
                selected_item = request.POST.get('selected')
                cursor = connection.cursor()
                sql = "SELECT MAX(ITEM_ID) FROM CART_ITEMS"
                cursor.execute(sql)
                cart_item_id = cursor.fetchone()[0]
                if cart_item_id is not None:
                    cart_item_id = cart_item_id + 1
                else:
                    cart_item_id = 1

                cursor = connection.cursor()
                sql = "SELECT FOOD_ID FROM FOOD WHERE NAME = %s"
                cursor.execute(sql,[selected_item])
                food_id = cursor.fetchone()[0]
                connection.close()

                cursor = connection.cursor()
                sql = "INSERT INTO CART_ITEMS VALUES(%s, %s, %s, %s)"
                cursor.execute(sql,[cart_item_id, cart_id, food_id,1])
                connection.close()

        selected_items = []
        cursor = connection.cursor()
        sql = "SELECT F.NAME FROM FOOD F JOIN CART_ITEMS C ON (F.FOOD_ID = C.FOOD_ID) WHERE C.CART_ID = %s"
        cursor.execute(sql,[cart_id])
        result = cursor.fetchall()
        connection.close()
        for row in result:
            selected_items.append(row[0].lower())

        cursor = connection.cursor()
        sql = "SELECT FOOD_ID, NAME ,PRICE, DESCRIPTION, PICTURE FROM FOOD WHERE LOWER(NAME) LIKE LOWER(%s) ORDER BY FOOD_ID"
        cursor.execute(sql, ["%"+search_str+"%"])
        result = cursor.fetchall()
        connection.close()
        dict = []

        for r in result:
            if r[1].lower() not in selected_items:
                id = r[0]
                name = r[1]
                price = r[2]
                des = r[3]
                pic = r[4]
                row = {'id':id, 'name':name, 'price':price,'des':des,'pic':pic}
                dict.append(row)

        return render(request, 'store/store.html', context = {'dict':dict})
    return redirect('nlview')


def cart(request):
    if request.session.has_key('customer_name'):
        name = request.session.get('customer_name')

        cursor = connection.cursor()
        sql = "SELECT CUSTOMER_ID FROM CUSTOMERS WHERE NAME = %s"
        cursor.execute(sql,[name])
        id = cursor.fetchone()[0]
        request.session['id'] = id
        connection.close()

        cursor = connection.cursor()
        sql = "SELECT CART_ID FROM CART WHERE CUSTOMER_ID = %s"
        cursor.execute(sql,[id])
        cart_id = cursor.fetchone()[0]
        connection.close()

        cursor = connection.cursor()
        sql = "SELECT FOOD_ID,QUANTITY FROM CART_ITEMS WHERE CART_ID = %s"
        cursor.execute(sql,[cart_id])
        result = cursor.fetchall()
        connection.close()
        f_ids = []
        dict = []
        for r in result:
            x = r[0]
            f_ids.append(x)
            quantity = r[1]
            cursor = connection.cursor()
            sql = "SELECT NAME,PRICE,PICTURE FROM FOOD WHERE FOOD_ID = %s"
            cursor.execute(sql,[x])
            result = cursor.fetchall()
            connection.close()

            for r in result:
                name = r[0]
                price = r[1]
                pic = r[2]
                row = {'id':x, 'name':name, 'price':price,'pic':pic,'quantity':quantity}
                dict.append(row)

        if request.method == "POST":
            for i in f_ids:
                quantity = request.POST.get(str(i))
                if quantity == '0':
                    cursor = connection.cursor()
                    sql = "DELETE FROM CART_ITEMS WHERE FOOD_ID = %s"
                    cursor.execute(sql,[i])
                    cursor = connection.cursor()
                else:
                    cursor = connection.cursor()
                    sql = "UPDATE CART_ITEMS SET quantity = %s WHERE FOOD_ID = %s;"
                    cursor.execute(sql,[quantity,i])
                    cursor = connection.cursor()
            return redirect('checkout')
        return render(request,'store/cart.html', context = {'dict':dict})
    return redirect('nlview')

def checkout(request):
    if request.session.has_key('customer_name'):
        name = request.session.get('customer_name')
        id = request.session.get('id')

        cursor = connection.cursor()
        total_bill = cursor.callfunc('TOTAL_BILL_ONLINE', float, [id])

        cursor = connection.cursor()
        sql = "SELECT FOOD_ID FROM CART_ITEMS WHERE CART_ID = %s"
        cursor.execute(sql,[id])
        result = cursor.fetchall()
        connection.close()
        dict = []
        for r in result:
            cursor = connection.cursor()
            sql = "SELECT NAME,PRICE,PICTURE FROM FOOD WHERE FOOD_ID = %s"
            cursor.execute(sql,[r[0]])
            result1 = cursor.fetchall()
            connection.close()
            cursor = connection.cursor()
            sql = "SELECT QUANTITY FROM CART_ITEMS WHERE FOOD_ID = %s and CART_ID = %s"
            cursor.execute(sql,[r[0],id])
            quantity = cursor.fetchone()[0]
            connection.close()

            for r in result1:
                name = r[0]
                price = r[1]
                pic = r[2]
                row = {'name':name, 'price':price,'pic':pic,'quantity':quantity}
                dict.append(row)

        if request.method == "POST":
            cursor = connection.cursor()
            sql = 'SELECT MAX(ITEM_ID) FROM ORDERED_ITEMS'
            cursor.execute(sql)
            item_id = cursor.fetchone()
            item_id = item_id[0]
            item_id = generate_primary_key(item_id)

            cursor = connection.cursor()
            sql = 'SELECT ON_ORDER_ID.NEXTVAL FROM dual;'
            cursor.execute(sql)
            order_id = cursor.fetchone()[0]
            order_id = 'ON_' + str(order_id)

            cursor = connection.cursor()
            sql = "SELECT FOOD_ID, QUANTITY FROM CART_ITEMS WHERE CART_ID = %s"
            cursor.execute(sql,[id])
            result = cursor.fetchall()
            connection.close()
            dict = []

            for r in result:
                cursor = connection.cursor()
                sql = "INSERT INTO ORDERED_ITEMS(ITEM_ID,ORDER_ID,FOOD_ID,QUANTITY) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, [item_id, order_id, r[0], r[1]])
                item_id = item_id+1
                connection.close()
            id = request.session.get('id')
            address = request.POST.get('address')

            cursor = connection.cursor()
            cursor.callproc('INSERT_ON_ORDER', [id, address, order_id])
            connection.close()

            return redirect('history')

        return render(request,'store/checkout.html', context = {'dict':dict,'bill':total_bill})

    return redirect('nlview')

def history(request):
    if request.session.has_key('customer_name'):
        name = request.session.get('customer_name')
        cursor = connection.cursor()
        sql = "SELECT CUSTOMER_ID FROM CUSTOMERS WHERE NAME = %s"
        cursor.execute(sql,[name])
        id = cursor.fetchone()[0]
        connection.close()
        dict1 = []
        dict = []
        cursor = connection.cursor()
        sql = "SELECT ORDER_ID,STATUS,TOTAL_BILL,DATE_TIME FROM ON_ORDER WHERE CUSTOMER_ID = %s ORDER BY DATE_TIME DESC"
        cursor.execute(sql,[id])
        result = cursor.fetchall()
        connection.close()
        for r in result:
            order_id = r[0]
            status = r[1]
            bill = r[2]
            date = r[3]
            row1 = {'order_id':order_id, 'status':status, 'bill':bill,'date':date}
            dict1.append(row1)
            cursor = connection.cursor()
            sql = "SELECT FOOD_ID,QUANTITY FROM ORDERED_ITEMS WHERE ORDER_ID = %s"
            cursor.execute(sql,[order_id])
            result = cursor.fetchall()
            connection.close()
            for r in result:
                food_id = r[0]
                quantity = r[1]
                cursor = connection.cursor()
                sql = "SELECT NAME,PRICE,PICTURE FROM FOOD WHERE FOOD_ID = %s"
                cursor.execute(sql,[food_id])
                result = cursor.fetchall()
                connection.close()
                for r in result:
                    name = r[0]
                    price = r[1]
                    pic = r[2]
                    row = {'name':name, 'price':price,'pic':pic,'quantity':quantity,'order_id':order_id}
                    dict.append(row)
        return render(request,'store/history.html', context = {'dict':dict,'dict1':dict1})
    return redirect('nlview')
