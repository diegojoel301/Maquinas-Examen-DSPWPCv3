#!/bin/bash

while true
do
	sudo python3 auto_cliente.py $ip_server
	sleep 5

	for pid in $(ps -ef | grep "firefox" | awk '{print $2}')
    do
		sudo kill -9 $(pgrep firefox)
	done
	
done
