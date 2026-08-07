from flask import Flask, render_template, request, redirect, url_for, session, get_flashed_messages, flash
import mysql.connector
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = 'annapurna123'

ADMIN_USER = 'admin'
ADMIN_PASS = 'admin123'
UPI_ID = 'annapurna@upi'


# HOME PAGE
@app.route('/')
def home():
    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()
    sql = "SELECT * FROM menu WHERE meal_date = %s AND meal_type = %s AND available = 1"

    cursor.execute(sql, (str(date.today()), 'breakfast'))
    rows = cursor.fetchall()
    breakfast = []
    for row in rows:
        breakfast.append({'id': row[0], 'item_name': row[3], 'price': row[4]})

    cursor.execute(sql, (str(date.today()), 'lunch'))
    rows = cursor.fetchall()
    lunch = []
    for row in rows:
        lunch.append({'id': row[0], 'item_name': row[3], 'price': row[4]})

    cursor.execute(sql, (str(date.today()), 'dinner'))
    rows = cursor.fetchall()
    dinner = []
    for row in rows:
        dinner.append({'id': row[0], 'item_name': row[3], 'price': row[4]})

    cursor.close()
    con.close()
    return render_template('index.html', breakfast=breakfast, lunch=lunch, dinner=dinner)


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    msgs = get_flashed_messages()
    msg = msgs[0] if msgs else ''

    if request.method == 'POST':
        NAME = request.form.get('name')
        EMAIL = request.form.get('email')
        PASSWORD = request.form.get('password')
        DIET = request.form.get('diet')

        con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
        cursor = con.cursor()
        sql = "INSERT INTO students (name, email, password, diet) VALUES (%s, %s, %s, %s)"
        values = (NAME, EMAIL, PASSWORD, DIET)
        try:
            cursor.execute(sql, values)
            con.commit()
            cursor.close()
            con.close()
            flash('Registered successfully. Please login.')
            return redirect(url_for('login'))
        except:
            flash('Email already exists.')
            msgs = get_flashed_messages()
            msg = msgs[0] if msgs else ''
        cursor.close()
        con.close()

    return render_template('register.html', msg=msg)


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    msgs = get_flashed_messages()
    msg = msgs[0] if msgs else ''

    if request.method == 'POST':
        EMAIL = request.form.get('email')
        PASSWORD = request.form.get('password')

        con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
        cursor = con.cursor()
        sql = "SELECT * FROM students WHERE email = %s AND password = %s"
        values = (EMAIL, PASSWORD)
        cursor.execute(sql, values)
        result = cursor.fetchone()
        cursor.close()
        con.close()

        if result:
            session['student_id'] = result[0]
            session['student_name'] = result[1]
            session['membership_type'] = result[5]
            session['membership_status'] = result[6]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.')
            msgs = get_flashed_messages()
            msg = msgs[0] if msgs else ''

    return render_template('login.html', msg=msg)


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# STUDENT DASHBOARD
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    msgs = get_flashed_messages()
    msg = msgs[0] if msgs else ''

    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()

    sql = "SELECT * FROM students WHERE id = %s"
    values = (session['student_id'],)
    cursor.execute(sql, values)
    result = cursor.fetchone()
    student = {
        'id': result[0],
        'name': result[1],
        'diet': result[4],
        'membership_type': result[5],
        'membership_status': result[6]
    }

    if request.method == 'POST':
        MENU_ID = request.form.get('menu_id')
        sql = "SELECT id FROM orders WHERE student_id = %s AND menu_id = %s AND order_date = %s"
        values = (session['student_id'], MENU_ID, str(date.today()))
        cursor.execute(sql, values)
        already = cursor.fetchone()
        if not already:
            sql = "INSERT INTO orders (student_id, menu_id, order_date) VALUES (%s, %s, %s)"
            values = (session['student_id'], MENU_ID, str(date.today()))
            cursor.execute(sql, values)
            con.commit()
            flash('Order confirmed!')
            msgs = get_flashed_messages()
            msg = msgs[0] if msgs else ''

    breakfast = []
    lunch = []
    dinner = []

    if student['membership_status'] == 'active':
        sql = "SELECT * FROM menu WHERE meal_date = %s AND meal_type = %s AND available = 1"

        if student['membership_type'] == 'gold':
            cursor.execute(sql, (str(date.today()), 'breakfast'))
            rows = cursor.fetchall()
            for row in rows:
                breakfast.append({'id': row[0], 'item_name': row[3], 'price': row[4]})

        cursor.execute(sql, (str(date.today()), 'lunch'))
        rows = cursor.fetchall()
        for row in rows:
            lunch.append({'id': row[0], 'item_name': row[3], 'price': row[4]})

        cursor.execute(sql, (str(date.today()), 'dinner'))
        rows = cursor.fetchall()
        for row in rows:
            dinner.append({'id': row[0], 'item_name': row[3], 'price': row[4]})

    sql = "SELECT menu_id FROM orders WHERE student_id = %s AND order_date = %s"
    values = (session['student_id'], str(date.today()))
    cursor.execute(sql, values)
    rows = cursor.fetchall()
    ordered = [row[0] for row in rows]

    cursor.close()
    con.close()

    return render_template('dashboard.html',
        student=student,
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner,
        ordered=ordered,
        msg=msg
    )


# PROFILE
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    msgs = get_flashed_messages()
    msg = msgs[0] if msgs else ''

    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()

    if request.method == 'POST':
        NAME = request.form.get('name')
        PHONE = request.form.get('phone')
        DIET = request.form.get('diet')
        sql = "UPDATE students SET name = %s, phone = %s, diet = %s WHERE id = %s"
        values = (NAME, PHONE, DIET, session['student_id'])
        cursor.execute(sql, values)
        con.commit()
        session['student_name'] = NAME
        flash('Profile updated successfully.')
        msgs = get_flashed_messages()
        msg = msgs[0] if msgs else ''

    sql = "SELECT * FROM students WHERE id = %s"
    values = (session['student_id'],)
    cursor.execute(sql, values)
    result = cursor.fetchone()
    student = {
        'name': result[1],
        'email': result[2],
        'diet': result[4],
        'phone': result[8] if len(result) > 8 and result[8] else ''
    }

    cursor.close()
    con.close()

    return render_template('profile.html', student=student, msg=msg)


# ORDER HISTORY (STUDENT)
@app.route('/orders')
def orders():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()
    sql = "SELECT o.id, o.order_date, m.item_name, m.price FROM orders o JOIN menu m ON o.menu_id = m.id WHERE o.student_id = %s ORDER BY o.order_date DESC, o.id DESC"
    values = (session['student_id'],)
    cursor.execute(sql, values)
    rows = cursor.fetchall()
    order_list = []
    for row in rows:
        order_list.append({'id': row[0], 'order_date': row[1], 'item_name': row[2], 'price': row[3]})

    sql = "SELECT id, item_names, total_amount, transaction_id, order_date, delivered FROM walkin_orders WHERE student_id = %s ORDER BY id DESC"
    values = (session['student_id'],)
    cursor.execute(sql, values)
    rows = cursor.fetchall()
    walkin_list = []
    for row in rows:
        walkin_list.append({'id': row[0], 'item_names': row[1], 'total_amount': row[2], 'transaction_id': row[3], 'order_date': row[4], 'delivered': row[5]})

    cursor.close()
    con.close()

    return render_template('order_history.html', orders=order_list, walkin_orders=walkin_list, today=str(date.today()))


# CANCEL A MEAL ORDER (student can only cancel today's own, undelivered order)
@app.route('/orders/cancel/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))

    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()
    sql = "DELETE FROM orders WHERE id = %s AND student_id = %s AND order_date = %s"
    values = (order_id, session['student_id'], str(date.today()))
    cursor.execute(sql, values)
    con.commit()
    cursor.close()
    con.close()

    flash('Order cancelled.')
    return redirect(url_for('orders'))


# MEMBERSHIP
@app.route('/membership', methods=['GET', 'POST'])
def membership():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    msgs = get_flashed_messages()
    msg = msgs[0] if msgs else ''

    if request.method == 'POST':
        PLAN = request.form.get('plan')
        TXN_ID = request.form.get('transaction_id')

        con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
        cursor = con.cursor()
        sql = "UPDATE students SET membership_type = %s, membership_status = 'pending', transaction_id = %s WHERE id = %s"
        values = (PLAN, TXN_ID, session['student_id'])
        cursor.execute(sql, values)
        con.commit()
        cursor.close()
        con.close()

        flash('Payment submitted. Waiting for admin approval.')
        msgs = get_flashed_messages()
        msg = msgs[0] if msgs else ''

    return render_template('membership.html', msg=msg, upi_id=UPI_ID)


# WALK-IN ORDER
@app.route('/walkin', methods=['GET', 'POST'])
def walkin():
    if 'student_id' not in session:
        flash('Please login to place a walk-in order.')
        return redirect(url_for('login'))

    msgs = get_flashed_messages()
    msg = msgs[0] if msgs else ''

    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()

    sql = "SELECT name, phone FROM students WHERE id = %s"
    cursor.execute(sql, (session['student_id'],))
    result = cursor.fetchone()
    student_name = result[0]
    student_phone = result[1] if result[1] else ''

    sql = "SELECT * FROM menu WHERE meal_date = %s AND meal_type = %s AND available = 1"

    cursor.execute(sql, (str(date.today()), 'breakfast'))
    rows = cursor.fetchall()
    breakfast = []
    for row in rows:
        breakfast.append({'id': row[0], 'item_name': row[3], 'price': row[4]})

    cursor.execute(sql, (str(date.today()), 'lunch'))
    rows = cursor.fetchall()
    lunch = []
    for row in rows:
        lunch.append({'id': row[0], 'item_name': row[3], 'price': row[4]})

    cursor.execute(sql, (str(date.today()), 'dinner'))
    rows = cursor.fetchall()
    dinner = []
    for row in rows:
        dinner.append({'id': row[0], 'item_name': row[3], 'price': row[4]})

    if request.method == 'POST':
        CUSTOMER_NAME = request.form.get('customer_name')
        PHONE = request.form.get('phone')
        selected_ids = request.form.getlist('item_ids')
        TXN_ID = request.form.get('transaction_id')

        if not CUSTOMER_NAME or not PHONE:
            flash('Please enter your name and phone number.')
            msgs = get_flashed_messages()
            msg = msgs[0] if msgs else ''
            cursor.close()
            con.close()
            return render_template('walkin.html', breakfast=breakfast, lunch=lunch, dinner=dinner, msg=msg, upi_id=UPI_ID, student_name=student_name, student_phone=student_phone)

        if not selected_ids:
            flash('Please select at least one item.')
            msgs = get_flashed_messages()
            msg = msgs[0] if msgs else ''
            cursor.close()
            con.close()
            return render_template('walkin.html', breakfast=breakfast, lunch=lunch, dinner=dinner, msg=msg, upi_id=UPI_ID, student_name=student_name, student_phone=student_phone)

        format_ids = ','.join(['%s'] * len(selected_ids))
        sql = f"SELECT item_name, price FROM menu WHERE id IN ({format_ids})"
        cursor.execute(sql, selected_ids)
        selected_rows = cursor.fetchall()

        TOTAL = 0
        item_names = []
        for row in selected_rows:
            item_names.append(row[0])
            TOTAL += row[1]

        sql = "INSERT INTO walkin_orders (student_id, customer_name, phone, item_names, total_amount, transaction_id, order_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (session['student_id'], CUSTOMER_NAME, PHONE, ', '.join(item_names), TOTAL, TXN_ID, str(date.today()))
        cursor.execute(sql, values)
        con.commit()
        ORDER_ID = cursor.lastrowid

        cursor.close()
        con.close()
        return render_template('walkin_confirm.html', order_id=ORDER_ID, total_amount=TOTAL, items=item_names)

    cursor.close()
    con.close()
    return render_template('walkin.html', breakfast=breakfast, lunch=lunch, dinner=dinner, msg=msg, upi_id=UPI_ID, student_name=student_name, student_phone=student_phone)


# ADMIN LOGIN
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    msgs = get_flashed_messages()
    msg = msgs[0] if msgs else ''

    if request.method == 'POST':
        USERNAME = request.form.get('username')
        PASSWORD = request.form.get('password')

        if USERNAME == ADMIN_USER and PASSWORD == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.')
            msgs = get_flashed_messages()
            msg = msgs[0] if msgs else ''

    return render_template('admin_login.html', msg=msg)


# ADMIN DASHBOARD
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    msgs = get_flashed_messages()
    msg = msgs[0] if msgs else ''

    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()

    # auto-clean menu items older than 30 days that were never ordered, keeps the table tidy
    # (items that were ordered are kept so order history still shows their name/price)
    cutoff = str(date.today() - timedelta(days=30))
    cursor.execute("DELETE m FROM menu m LEFT JOIN orders o ON o.menu_id = m.id WHERE m.meal_date < %s AND o.id IS NULL", (cutoff,))
    con.commit()

    sql = "SELECT m.meal_type, m.item_name, COUNT(o.id) FROM orders o JOIN menu m ON o.menu_id = m.id WHERE o.order_date = %s GROUP BY m.meal_type, m.item_name"
    values = (str(date.today()),)
    cursor.execute(sql, values)
    rows = cursor.fetchall()
    headcount = []
    for row in rows:
        headcount.append({'meal_type': row[0], 'item_name': row[1], 'total': row[2]})

    sql = "SELECT id, name, membership_type FROM students WHERE membership_status = 'active' ORDER BY membership_type, name"
    cursor.execute(sql)
    rows = cursor.fetchall()
    active_members = []
    silver_count = 0
    gold_count = 0
    for row in rows:
        active_members.append({'id': row[0], 'name': row[1], 'membership_type': row[2]})
        if row[2] == 'silver':
            silver_count = silver_count + 1
        if row[2] == 'gold':
            gold_count = gold_count + 1
    total_active = silver_count + gold_count

    sql = "SELECT * FROM students WHERE membership_status = 'pending'"
    cursor.execute(sql)
    rows = cursor.fetchall()
    pending = []
    for row in rows:
        pending.append({'id': row[0], 'name': row[1], 'email': row[2], 'membership_type': row[5], 'transaction_id': row[7]})

    sql = "SELECT id, customer_name, phone, item_names, total_amount, transaction_id FROM walkin_orders WHERE order_date = %s AND delivered = 0 ORDER BY id DESC"
    values = (str(date.today()),)
    cursor.execute(sql, values)
    rows = cursor.fetchall()
    walkin_orders = []
    for row in rows:
        walkin_orders.append({'id': row[0], 'customer_name': row[1], 'phone': row[2], 'item_names': row[3], 'total_amount': row[4], 'transaction_id': row[5]})

    sql = "SELECT id, meal_type, item_name, price, available FROM menu WHERE meal_date = %s ORDER BY meal_type, item_name"
    values = (str(date.today()),)
    cursor.execute(sql, values)
    rows = cursor.fetchall()
    todays_menu = []
    for row in rows:
        todays_menu.append({'id': row[0], 'meal_type': row[1], 'item_name': row[2], 'price': row[3], 'available': row[4]})

    cursor.close()
    con.close()

    return render_template('admin_dashboard.html',
        headcount=headcount,
        pending=pending,
        walkin_orders=walkin_orders,
        todays_menu=todays_menu,
        today=date.today(),
        msg=msg
    )


# ADMIN ACTIVATE
@app.route('/admin/activate/<int:student_id>', methods=['POST'])
def activate(student_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()
    sql = "UPDATE students SET membership_status = 'active' WHERE id = %s"
    values = (student_id,)
    cursor.execute(sql, values)
    con.commit()
    cursor.close()
    con.close()

    flash('Membership activated.')
    return redirect(url_for('admin_dashboard'))


# ADMIN REJECT
@app.route('/admin/reject/<int:student_id>', methods=['POST'])
def reject(student_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()
    sql = "UPDATE students SET membership_status = 'rejected', membership_type = 'none' WHERE id = %s"
    values = (student_id,)
    cursor.execute(sql, values)
    con.commit()
    cursor.close()
    con.close()

    flash('Membership rejected.')
    return redirect(url_for('admin_dashboard'))


# ADMIN - MARK WALK-IN ORDER DELIVERED
@app.route('/admin/walkin/deliver/<int:order_id>', methods=['POST'])
def deliver_walkin(order_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()
    sql = "UPDATE walkin_orders SET delivered = 1 WHERE id = %s"
    values = (order_id,)
    cursor.execute(sql, values)
    con.commit()
    cursor.close()
    con.close()

    flash('Order marked as delivered.')
    return redirect(url_for('admin_dashboard'))


# ADMIN - TOGGLE MENU ITEM AVAILABILITY (e.g. item ran out mid-day)
@app.route('/admin/menu/toggle/<int:menu_id>', methods=['POST'])
def toggle_menu_item(menu_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()
    sql = "UPDATE menu SET available = 1 - available WHERE id = %s"
    values = (menu_id,)
    cursor.execute(sql, values)
    con.commit()
    cursor.close()
    con.close()

    flash('Menu item updated.')
    return redirect(url_for('admin_dashboard'))


# ADMIN - ALL ORDERS
@app.route('/admin/orders')
def admin_orders():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
    cursor = con.cursor()
    sql = "SELECT o.id, s.name, m.item_name, m.meal_type, o.order_date FROM orders o JOIN students s ON o.student_id = s.id JOIN menu m ON o.menu_id = m.id ORDER BY o.order_date DESC, o.id DESC"
    cursor.execute(sql)
    rows = cursor.fetchall()
    all_orders = []
    for row in rows:
        all_orders.append({'id': row[0], 'student_name': row[1], 'item_name': row[2], 'meal_type': row[3], 'order_date': row[4]})
    cursor.close()
    con.close()

    return render_template('admin_orders.html', all_orders=all_orders)


# ADMIN ADD MENU
@app.route('/admin/add_menu', methods=['GET', 'POST'])
def add_menu():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    msgs = get_flashed_messages()
    msg = msgs[0] if msgs else ''

    if request.method == 'POST':
        MEAL_DATE = request.form.get('meal_date')
        MEAL_TYPE = request.form.get('meal_type')
        ITEM_NAME = request.form.get('item_name')
        PRICE = request.form.get('price')

        con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
        cursor = con.cursor()
        sql = "INSERT INTO menu (meal_date, meal_type, item_name, price) VALUES (%s, %s, %s, %s)"
        values = (MEAL_DATE, MEAL_TYPE, ITEM_NAME, PRICE)
        cursor.execute(sql, values)
        con.commit()
        cursor.close()
        con.close()

        flash('Menu item added.')
        msgs = get_flashed_messages()
        msg = msgs[0] if msgs else ''

    return render_template('add_menu.html', msg=msg, today=str(date.today()))


# ADMIN BULK ADD MENU
@app.route('/admin/bulk_menu', methods=['GET', 'POST'])
def bulk_menu():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    msgs = get_flashed_messages()
    msg = msgs[0] if msgs else ''

    if request.method == 'POST':
        item_names = request.form.getlist('item_name')
        meal_types = request.form.getlist('meal_type')
        prices = request.form.getlist('price')

        con = mysql.connector.connect(host='localhost', user='root', password='', database='mess_db')
        cursor = con.cursor()

        count = 0
        for i in range(len(item_names)):
            if item_names[i] and prices[i]:
                sql = "INSERT INTO menu (meal_date, meal_type, item_name, price) VALUES (%s, %s, %s, %s)"
                values = (str(date.today()), meal_types[i], item_names[i], prices[i])
                cursor.execute(sql, values)
                count += 1

        con.commit()
        cursor.close()
        con.close()

        flash(str(count) + ' items added for today.')
        msgs = get_flashed_messages()
        msg = msgs[0] if msgs else ''

    return render_template('bulk_menu.html', msg=msg, today=str(date.today()))


if __name__ == '__main__':
    app.run(debug=True)
