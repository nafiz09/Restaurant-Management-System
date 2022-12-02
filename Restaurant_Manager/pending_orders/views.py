from django.shortcuts import render, redirect
from django.db import connection

# Create your views here.
def pending_list(request):
    if request.session.has_key('admin_name'):
        if request.method == "POST":
            id = request.POST.get('id')
            cursor = connection.cursor()
            sql = "UPDATE ON_ORDER SET STATUS = 'ACCEPTED' WHERE ORDER_ID = %s"
            cursor.execute(sql, [id])
            connection.close()

        cursor = connection.cursor()
        sql = "SELECT ORDER_ID, C.NAME, DELIVARY_ADDRESS, DATE_TIME, TOTAL_BILL FROM ON_ORDER O JOIN CUSTOMERS C ON (O.CUSTOMER_ID = C.CUSTOMER_ID) WHERE LOWER(O.STATUS) = 'pending' ORDER BY DATE_TIME"
        cursor.execute(sql)
        result = cursor.fetchall()
        connection.close()

        dict = []

        for r in result:
            order_id = r[0]
            customer_name = r[1]
            address = r[2]
            date_time = r[3]
            total_bill = r[4]

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

            row = {'order_id':order_id, 'customer_name':customer_name, 'address':address, 'date_time':date_time, 'total_bill':total_bill, 'ordered_items':ordered_items}
            dict.append(row)

        return render(request, "pending_orders/pending_list.html", context={'dict':dict})

    return redirect('not_lgin_view')
