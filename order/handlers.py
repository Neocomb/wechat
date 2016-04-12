#!/usr/bin/env python
# encoding: utf-8

from order.models import User, Lesson, Room, Order
from order.webapp import app
from flask import render_template, request, jsonify
from flask import abort, session, redirect, url_for
from functools import wraps
from datetime import * 
import time

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('user_login'))
        else:
            return f(*args, **kwargs)

    return decorated_function


@app.route('/order/user', methods=['GET'])
def user_login():
    return render_template('/login.html')


@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
        return render_template('/login.html')
    else:
        return render_template('/login.html')


@app.route('/order/user/register', methods=['GET'])
def user_register():
    return render_template('/register.html')


@app.route('/order/user/register', methods=['POST'])
def user_register_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return redirect('/order/user')

    user = User(username=username, password=password)
    user.save()
    return redirect('/order/user')


@app.route('/order/user', methods=['POST'])
def user_login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return redirect('/order/user')

    if User.load_one(username, password):
        session['username'] = username
        return redirect('/order/index')
    else:
        return redirect('/order/user')


@app.route('/', methods=['get'])
@app.route('/order/index', methods=['GET'])
@login_required
def index():
    times = [
        "第一节","第二节","第三节","第四节","第五节","第六节","第七节",
    ]
    weeks = [
        "第一周","第二周","第三周","第四周","第五周","第六周","第七周","第八周",
        "第九周","第十周","第十一周","第十二周","第十三周","第十四周","第十五周","第十六周",
    ]
    days = [
        "周一","周二","周三","周四","周五","周六","周日",
    ]
    classrooms = [
        "SX105","SX106","SX107","SX201","SX202","SX203","SX204","SX205","SX302","SX303","SX304",
        "SX305","SX401","SX402","SX404","SX405","SX406","SX407","SX501","SX502","SX503","SX504",
        "SX505","SX506","SX507",
    ]
    subjects = [
        "力学","电磁学","热学","振动与波","光学","近代与综合"
    ]

    return render_template('index.html', times=times, weeks=weeks, days=days, classrooms=classrooms, subjects=subjects)


@app.route('/wx/order/equipment', methods=['get'])
@login_required
def get_equipment():
    
    week = request.args.get("week")
    day = request.args.get("day")
    time = request.args.get("time")
    classroom = request.args.get("classroom")
    subject = request.args.get("subject")

    if week:
        session['week'] = week
    if day:
        session['day'] = day
    if time:
        session['time'] = time
    if classroom:
        session['classroom'] = classroom
    if subject:
        session['subject'] = subject

    lessons = Lesson.load_by_subject(subject)
    # return lessons
    return render_template("getlesson.html", week=week, subject=subject, day=day, time=time, classroom=classroom,lessons=lessons)


@app.route('/wx/order/history')
@login_required
def get_history():
    username = session['username']
    orders = Order.load_user(username)
    return render_template("account.html", orders=orders)


@app.route('/wx/order/order')
@login_required
def get_order():
    # lesson = request.args.get("lesson")
    # lesson_num = request.args.get("lesson_num")
    lessons = request.args.get("lessons")
    order_date = calculate_date(session['week'],session['day'])
    now_date = datetime.today()
    if lessons and session['week'] and session['day'] and session['time'] and session['classroom'] and session['subject']:
        order = {
            'week' : session['week'],
            'day' : session['day'],
            'time' : session['time'],
            'classroom' : session['classroom'],
            'subject' : session['subject'],
            'lessons' : lessons,
            'username' : session['username'],
            'order_date':order_date,
            'now_date':now_date
        }
        
        Order(lessons=lessons,  week=session['week'], day=session['day'], time=session['time'], classroom=session['classroom'], subject=session['subject'], user=session['username'],order_date=order_date,now_date=now_date).save()
        session['week'] = None
        session['day'] = None
        session['time'] = None
        session['classroom'] = None
        session['subject'] = None

    return render_template('order.html', order = order)


def calculate_date(week,day):
    firstday = datetime(2016, 2, 29)
     
    week_dict ={'第一周':1,'第二周':2,'第三周':3,'第四周':4,'第五周':5,'第六周':6,'第七周':7,'第八周':8,'第九周':9,'第十周':10,'第十一周':11,'第十二周':12,'第十三周':13,'第十四周':14,'第十五周':15,'第十六周':16}
    day_dict ={'周一':1,'周二':2,'周三':3,'周四':4,'周五':5,'周六':6,'周日':7}
    
    week_digit = week_dict.get(week)
    day_digit = day_dict.get(day)
    # days =  (week_dict-1)*7+(day_digit-1)
    days = week_digit*7+day_digit-8
    order_date = firstday + timedelta(days=days)
    return order_date


@app.route('/order/filter', methods=['get'])
@login_required
def filtrate_date():
    startdate = request.args.get('startdate')[0:10]
    enddate = request.args.get('enddate')[0:10]

    x = datetime.utcfromtimestamp(float(startdate))
    y = datetime.utcfromtimestamp(float(enddate))
    
    orders_with_filter = Order.filter_date(x, y, session['username'])

    return render_template("account.html",orders=orders_with_filter)



@app.route('/admin/login', methods=['GET'])
def admin_login():
    return render_template('/admin/admin_login.html')


@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return redirect('/admin/user')

    if User.load_one(username, password):
        session['username'] = username
        return redirect('/admin/user')
    else:
        return redirect('/admin/user')


@app.route('/admin/logout')
def admin_logout():
    if 'username' in session:
        session.pop('username', None)
        return render_template('/admin/admin_login.html')
    else:
        return render_template('/admin/admin_login.html')


@app.route('/admin/order', methods=['get'])
@login_required
def admin_order():
    startdate = request.args.get('startdate')
    enddate = request.args.get('enddate')
    username = request.args.get('username')
    users = User.load_all()

    if username:
        # pprint.pprint(username)
        orders = Order.load_user(username)
        # pprint.pprint(orders)
    elif startdate:
        # pprint.pprint(startdate)
        x = datetime.utcfromtimestamp(float(startdate[0:10]))
        y = datetime.utcfromtimestamp(float(enddate[0:10]))
        orders = Order.filter_date(x, y,'')
    else:
        orders = Order.load_all()
    return render_template("admin/admin_order.html", orders=orders,users=users)


@app.route('/admin/user', methods=['get'])
@login_required
def admin_user():
    users = User.load_all()
    return render_template("admin/admin_user.html", users=users)
