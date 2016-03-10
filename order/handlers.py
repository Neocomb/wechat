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


@app.route('/order/user/register', methods=['GET'])
def user_register():
    return render_template('/register.html')


@app.route('/order/user/register', methods=['POST'])
def user_register_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return redirect('/order/user/register')

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


@app.route('/', methods=['GET', 'POST'])
def home():
    return "<a href='/index'>预定</a>"


@app.route('/index', methods=['GET', 'POST'])
@app.route('/order/index', methods=['GET'])
@login_required
def index():
    return render_template('index.html')


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
        "8:00  : 10:00",
        "10:00 : 12:00",
        "12:00 : 14:00",
        "14:00 : 16:00",
    ]
    return render_template("time.html", times=times)


@app.route('/wx/order/order')
@login_required
def get_order():
    lesson = request.args.get("lesson")
    if lesson and session['time'] and session['place']:
        Order(time=session['time'], place=session['place'], lesson=lesson, user=session['username']).save()
        session['time'] = None
        session['place'] = None

    return render_template('order.html', orders=Order.load_user(session['username']))
