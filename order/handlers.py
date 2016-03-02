from datetime import time

from order import wechat
from order.models import User
from order.webapp import app
from flask import render_template, request, jsonify
from flask import abort, session, redirect, url_for
from functools import wraps



def handle_message_text(msg):
    resp = wechat.make_base_reply_message_from_message(msg)
    resp.update({
        'MsgType': 'text',
        'CreateTime': int(time.time()),
        'Content': msg['Content'],
    })
    return wechat.dict_to_xml_string(resp)


@app.route('/wx/event', methods=['POST'])
def handle_event():
    if not app.testing:
        wechat.validate_message(request)
    echostr = request.args.get('echostr', '')
    if echostr:
        return echostr
    msg = wechat.xml_string_to_dict(request.data.decode(wechat.DEFAULT_ENCODING))
    if msg['MsgType'] == 'text':
        return handle_message_text(msg)
    else:
        return ''


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
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        abort(400)

    if User.load_one(username, password):
        session['username'] = username
        return redirect('/order/index')
    else:
        return render_template('/login.html')


@app.route('/order/user', methods=['put'])
def user_registe():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        abort(400)
    # validate name and password
    # isUsernameValidate(username)
    # isPasswordValidate(password)

    user = User(username=username, password=password)
    user.save()

    return render_template('/login.html')


@app.route('/order/index', methods=['GET'])
def index():
    return "hello world"