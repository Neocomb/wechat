#!/bin/bash
curl -G -m 2 http://www.wlysstyy.cn/
if [ $? != 0  ]
then
    ssh root@139.129.6.17
    /root/source/wechat/start.sh
fi
