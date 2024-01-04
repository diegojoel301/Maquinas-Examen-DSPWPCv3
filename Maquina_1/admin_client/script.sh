#!/bin/bash

while true
do
	sudo python3 auto_cliente.py $ip_server
	curl -L "http://$ip_server:5000/delete"
	sleep 10

	for pid in $(ps -ef | grep "firefox" | awk '{print $2}')
    do
		sudo kill -9 $(pgrep firefox)
	done
	
done
