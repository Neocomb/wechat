
su wechat
ps | grep python | awk '{print $1}'| xargs -r kill -9
PYTHONPATH=. python3.5 order/startup.py  2>err.log
