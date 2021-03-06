#!/bin/bash

ssh_tag=$1
session_id=$2
echo "----$ssh_tag---"

for i in $(seq 1 30);do
     process_id=$(ps -ef |grep $ssh_tag|grep -v sshpass |grep -v grep |grep -v  $0 | awk '{ print $2 }'  )
     echo "---process id: $process_id ---"
     if [ ! -z $process_id  ];then
         echo 'running str4ack'
         log_path=/usr/local/CrazyEye/log/`date +%F`
         mkdir -p $log_path
         sudo strace -fp $process_id  -t -o $log_path/session_$session_id.log
         break;
     fi;
     sleep 1;
done;
