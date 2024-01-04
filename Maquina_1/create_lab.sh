#!/bin/bash

# Para limpiar:
function clean()
{
    docker stop client_machine_1_dspwpcv3_container &&
    docker rm client_machine_1_dspwpcv3_container &&
    docker stop machine_1_dspwpcv3_container &&
    docker rm machine_1_dspwpcv3_container
}

docker build -t machine_1_dspwpcv3 .

docker rm machine_1_dspwpcv3_container
docker rm client_machine_1_dspwpcv3_container

docker run -p 35243:5000 --name machine_1_dspwpcv3_container -d -it machine_1_dspwpcv3

docker exec -it machine_1_dspwpcv3_container service vsftpd restart

ip_address=$(docker container inspect machine_1_dspwpcv3_container | grep -i "ipaddress" | tr ' ' '\n'  | tr -d '",' | grep -E "[0-9]+" | sort -u)

sed -i "s/[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+/$ip_address/g" admin_client/dockerfile

docker build -t client_machine_1_dspwpcv3 admin_client/.

docker run --name client_machine_1_dspwpcv3_container -d -it client_machine_1_dspwpcv3

docker exec -d -it client_machine_1_dspwpcv3_container ./script.sh

echo "[+] Ip victima: $ip_address"


