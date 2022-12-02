from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from datetime import date
# Create your views here.


def show_order_list(request):
    if request.session.has_key('admin_name'):
        from_date = date.today().strftime("%Y-%m-%d")
        to_date = date.today().strftime("%Y-%m-%d")
        order_type = "All"


        if request.method == "POST":
            if request.POST.get('view_order'):
                request.session['view_detail_id'] = request.POST.get('view_order')
                return redirect('view_detail_order')
            if request.POST.get("from_date"):
                from_date = str(request.POST.get("from_date"))
            if request.POST.get("to_date"):
                to_date = str(request.POST.get("to_date"))
            order_type = request.POST.get("type")

        dict = []
        total_sale = 0

        if order_type == "All" or order_type == "Dine-In Orders":
            cursor = connection.cursor()
            sql = "SELECT DATE_TIME, ORDER_ID, TABLE_NO, M.NAME, E.NAME, TOTAL_BILL FROM OFF_ORDER O JOIN MANAGER M ON (M.MANAGER_ID = O.MANAGER_ID) JOIN EMPLOYEES E ON (E.EMPLOYEE_ID = O.EMPLOYEE_ID) WHERE DATE_TIME >= TO_DATE(%s, 'YYYY-MM-DD') AND DATE_TIME <= TO_DATE(%s, 'YYYY-MM-DD')+1 ORDER BY DATE_TIME"
            cursor.execute(sql, [from_date, to_date])
            result = cursor.fetchall()
            connection.close()

            for r in result:
                time_stamp = r[0]
                order_id = r[1]
                table = r[2]
                manager = r[3]
                waiter = r[4]
                total = r[5]
                total_sale = total_sale + float(total)
                row = {'time_stamp':time_stamp, 'order_id':order_id, 'table':table, 'manager':manager, 'waiter':waiter, 'total':total}
                dict.append(row)

        if order_type == "All" or order_type == "Home Delivery Orders":
            cursor = connection.cursor()
            sql = "SELECT DATE_TIME, ORDER_ID, CUSTOMER_ID, TOTAL_BILL FROM ON_ORDER WHERE DATE_TIME >= TO_DATE(%s, 'YYYY-MM-DD') AND DATE_TIME <= TO_DATE(%s, 'YYYY-MM-DD')+1 AND STATUS = 'ACCEPTED' ORDER BY DATE_TIME "
            cursor.execute(sql, [from_date, to_date])
            result = cursor.fetchall()
            connection.close()

            for r in result:
                time_stamp = r[0]
                order_id = r[1]
                table = r[2]
                manager = "N/A"
                waiter = "N/A"
                total = r[3]
                total_sale = total_sale + float(total)
                row = {'time_stamp':time_stamp, 'order_id':order_id, 'table':table, 'manager':manager, 'waiter':waiter, 'total':total}
                dict.append(row)

        return render(request, "sales/sales_table.html", context={'dict':dict, 'from':from_date, 'to':to_date, "total_sale":total_sale, 'type':order_type})
    return redirect('not_lgin_view')


def order_details(request):
    if request.session.has_key('admin_name'):
        order_id = request.session.pop('view_detail_id')
        order_type = order_id.split('_')[0]
        if order_type == 'ON':
            cursor = connection.cursor()
            sql = "SELECT ORDER_ID, C.NAME, DELIVARY_ADDRESS, DATE_TIME, TOTAL_BILL FROM ON_ORDER O JOIN CUSTOMERS C ON (O.CUSTOMER_ID = C.CUSTOMER_ID) WHERE O.ORDER_ID = %s"
            cursor.execute(sql, [order_id])
            result = cursor.fetchone()
            connection.close()

            order_id = result[0]
            customer_name = result[1]
            address = result[2]
            date_time = result[3]
            total_bill = result[4]

            cursor = connection.cursor()
            sql = "SELECT F.NAME, O.QUANTITY, F.PRICE FROM FOOD F JOIN ORDERED_ITEMS O ON (F.FOOD_ID = O.FOOD_ID) WHERE O.ORDER_ID = %s"
            cursor.execute(sql, [order_id])
            r = cursor.fetchall()
            connection.close()

            ordered_items = []
            for items in r:
                item_name = items[0]
                quantity = items[1]
                unit_price = items[2]
                total = unit_price * quantity

                item = {'item_name':item_name, 'quantity':quantity, 'unit_price':unit_price, 'total':total}
                ordered_items.append(item)

            row = {'type':"ON", 'order_id':order_id, 'customer_name':customer_name, 'address':address, 'date_time':date_time, 'total_bill':total_bill, 'ordered_items':ordered_items}

        else:
            cursor = connection.cursor()
            sql = "SELECT DATE_TIME, ORDER_ID, TABLE_NO, M.NAME, E.NAME, TOTAL_BILL FROM OFF_ORDER O JOIN MANAGER M ON (M.MANAGER_ID = O.MANAGER_ID) JOIN EMPLOYEES E ON (E.EMPLOYEE_ID = O.EMPLOYEE_ID) WHERE O.ORDER_ID = %s"
            cursor.execute(sql, [order_id])
            result = cursor.fetchone()
            connection.close()

            date_time = result[0]
            order_id = result[1]
            table_no = result[2]
            manager_name = result[3]
            waiter_name = result[4]
            total_bill = result[5]

            cursor = connection.cursor()
            sql = "SELECT F.NAME, O.QUANTITY, F.PRICE FROM FOOD F JOIN ORDERED_ITEMS O ON (F.FOOD_ID = O.FOOD_ID) WHERE O.ORDER_ID = %s"
            cursor.execute(sql, [order_id])
            r = cursor.fetchall()
            connection.close()

            ordered_items = []
            for items in r:
                item_name = items[0]
                quantity = items[1]
                unit_price = items[2]
                total = unit_price * quantity

                item = {'item_name':item_name, 'quantity':quantity, 'unit_price':unit_price, 'total':total}
                ordered_items.append(item)

            row = {'type':"OFF", 'order_id':order_id, 'table_no':table_no, 'manager':manager_name,'waiter':waiter_name, 'date_time':date_time, 'total_bill':total_bill, 'ordered_items':ordered_items}

        return render(request, "sales/order_details.html", context={'dict':row})
    return redirect('not_lgin_view')
