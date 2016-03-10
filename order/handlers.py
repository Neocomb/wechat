from order.models import User, Lesson, Room, Order
from order.webapp import app
from flask import render_template, request, jsonify
from flask import abort, session, redirect, url_for
from functools import wraps


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
        abort(400)

    user = User(username=username, password=password)
    user.save()
    return redirect('/order/user')


@app.route('/order/user', methods=['POST'])
def user_login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        abort(400)

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
    lesson = request.args.get("lesson")
    lesson_num = request.args.get("lesson_num")

    if lesson and lesson_num and session['week'] and session['day'] and session['time'] and session['classroom'] and session['subject']:
        order = {
            'week' : session['week'],
            'day' : session['day'],
            'time' : session['time'],
            'classroom' : session['classroom'],
            'subject' : session['subject'],
            'lesson' : lesson,
            'lesson_num' : lesson_num,
            'username' : session['username']
        }
        Order(lesson_num=lesson_num, week=session['week'], day=session['day'], time=session['time'], classroom=session['classroom'], subject=session['subject'], lesson=lesson, user=session['username']).save()
        session['week'] = None
        session['day'] = None
        session['time'] = None
        session['classroom'] = None
        session['subject'] = None


    return render_template('order.html', order = order)


@app.route('/wx/order/room', methods=['get'])
@login_required
def get_room():
    building = request.args.get("building")

    if not building:
        rooms = Room.load_all()
    else:
        rooms = Room.load_by_building(building)

    subs = set()
    for room in Room.load_all():
        subs.add(room.building)

    return render_template("rooms.html", rooms=rooms, buildings=subs)


@app.route('/wx/order/lesson', methods=['get'])
@login_required
def get_lesson():
    subject = request.args.get("subject")
    time = request.args.get("time")

    if time:
        session['time'] = time

    if not subject:
        lessons = Lesson.load_all()
    else:
        lessons = Lesson.load_by_subject(subject)

    subs = set()
    for les in Lesson.load_all():
        subs.add(les.subject)

    return render_template("lesson.html", lessons=lessons, subjects=subs)


@app.route('/wx/order/time')
@login_required
def get_time():
    place = request.args.get("place")
    if place:
        session['place'] = place

    times = [
        "第一节","第二节","第三节","第四节","第五节","第六节","第七节",
    ]
    return render_template("time.html", times=times)


@app.route('/test/account', methods=['GET'])
def test_account():
    return render_template('/account.html')
