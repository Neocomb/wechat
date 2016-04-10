#!/bin/bash
curl -G -m 2 localhost
if [ $? != 0  ]
then
    echo "restart wechat"
    su wechat
    . ./start.sh >> check.log 2>&1 &
fi
