from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from datetime import date

# Create your views here.
def expenses_list(request):
    if request.session.has_key('admin_name'):
        from_date = date.today().strftime("%Y-%m-%d")
        to_date = date.today().strftime("%Y-%m-%d")
        expense_type = "All"
        total_expense = 0;

        cursor = connection.cursor()
        sql = "SELECT CATEGORY_ID, CATEGORY_NAME FROM EXPENSE_CATEGORY"
        cursor.execute(sql)
        result = cursor.fetchall()
        connection.close()
        dict = []
        for row in result:
            r = {'id':row[0], 'type':row[1]}
            dict.append(r)

        if request.method == "POST":
            if request.POST.get("from_date"):
                from_date = str(request.POST.get("from_date"))
            if request.POST.get("to_date"):
                to_date = str(request.POST.get("to_date"))
            expense_type = request.POST.get("type")

        cursor = connection.cursor()
        if expense_type == "All":
            sql = "SELECT DATE_ADDED, M.NAME, E.CATEGORY_NAME, DESCRIPTION, AMOUNT FROM EXPENSES EX JOIN MANAGER M ON (M.MANAGER_ID = EX.MANAGER_ID) JOIN EXPENSE_CATEGORY E ON (EX.CATEGORY = E.CATEGORY_ID) WHERE EX.DATE_ADDED >= TO_DATE(%s, 'YYYY-MM-DD') AND EX.DATE_ADDED <= TO_DATE(%s, 'YYYY-MM-DD')+1 ORDER BY DATE_ADDED"
            cursor.execute(sql, [from_date, to_date])
        else:
            sql = "SELECT DATE_ADDED, M.NAME, E.CATEGORY_NAME, DESCRIPTION, AMOUNT FROM EXPENSES EX JOIN MANAGER M ON (M.MANAGER_ID = EX.MANAGER_ID) JOIN EXPENSE_CATEGORY E ON (EX.CATEGORY = E.CATEGORY_ID) WHERE EX.CATEGORY = %s AND EX.DATE_ADDED >= TO_DATE(%s, 'YYYY-MM-DD') AND EX.DATE_ADDED <= TO_DATE(%s, 'YYYY-MM-DD')+1 ORDER BY DATE_ADDED"
            cursor.execute(sql, [expense_type, from_date, to_date])
        results = cursor.fetchall()
        connection.close()

        dict2 = []
        for r in results:
            row = {'date':r[0], 'manager':r[1], 'category':r[2], 'desc':r[3], 'amount':r[4]}
            total_expense = total_expense + float(r[4])
            dict2.append(row)

        return render(request, "expenses/expenses_list.html", context={'dict':dict, 'dict2':dict2, 'from':from_date, 'to':to_date, 'type':expense_type, 'total_expense':total_expense})

    return redirect('not_lgin_view')

def add_entry(request):
    if request.session.has_key('admin_name'):
        if request.method == "POST":
            if request.POST.get('form1'):
                category_id = request.POST.get('category')

                man_name = request.session.get('admin_name')
                cursor = connection.cursor()
                sql = "SELECT MANAGER_ID FROM MANAGER WHERE NAME = %s"
                cursor.execute(sql, [man_name])
                man_id = cursor.fetchone()[0]

                cursor = connection.cursor()
                sql = 'SELECT MAX(EXPENSE_ID) FROM EXPENSES'
                cursor.execute(sql)
                last_id = cursor.fetchone()
                last_id = last_id[0]
                if last_id is not  None:
                    expense_id = last_id + 1
                else:
                    expense_id = 1

                amount = request.POST.get('amount')
                desc = request.POST.get('description')

                cursor = connection.cursor()
                sql = "INSERT INTO EXPENSES VALUES (%s, %s, %s, %s, %s, SYSDATE)"
                cursor.execute(sql, [expense_id, man_id, category_id, amount, desc])
                connection.close()

                redirect('expenses')

            if request.POST.get('form2'):
                cursor = connection.cursor()
                sql = 'SELECT MAX(CATEGORY_ID) FROM EXPENSE_CATEGORY'
                cursor.execute(sql)
                last_id = cursor.fetchone()
                last_id = last_id[0]
                if last_id is not  None:
                    category_id = last_id + 1
                else:
                    category_id = 1

                category_name = request.POST.get('new_cat')

                cursor = connection.cursor()
                sql = "INSERT INTO EXPENSE_CATEGORY VALUES (%s, %s)"
                cursor.execute(sql, [category_id, category_name])
                connection.close()


        cursor = connection.cursor()
        sql = "SELECT CATEGORY_ID, CATEGORY_NAME FROM EXPENSE_CATEGORY"
        cursor.execute(sql)
        result = cursor.fetchall()
        connection.close()
        dict = []
        for row in result:
            r = {'id':row[0], 'type':row[1]}
            dict.append(r)

        return render(request, "expenses/add_entry.html", context={'dict':dict})
    return redirect('not_lgin_view')
