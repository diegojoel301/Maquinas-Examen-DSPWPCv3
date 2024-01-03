#!/bin/bash

# Para limpiar:
function clean()
{
    docker stop client_lab_1_dspwpcv2_container &&
    docker rm client_lab_1_dspwpcv2_container &&
    docker stop lab_1_dspwpcv2_container &&
    docker rm lab_1_dspwpcv2_container
}

docker build -t lab_1_dspwpcv2 .

docker rm lab_1_dspwpcv2_container
docker rm client_lab_1_dspwpcv2_container

docker run -p 5000:5000 -p 21:21 --name lab_1_dspwpcv2_container -d -it lab_1_dspwpcv2

docker exec -it lab_1_dspwpcv2_container service vsftpd restart

ip_address=$(docker container inspect lab_1_dspwpcv2_container | grep -i "ipaddress" | tr ' ' '\n'  | tr -d '",' | grep -E "[0-9]+" | sort -u)

sed -i "s/[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+/$ip_address/g" admin_client/dockerfile

docker build -t client_lab_1_dspwpcv2 admin_client/.

docker run --name client_lab_1_dspwpcv2_container -d -it client_lab_1_dspwpcv2

docker exec -d -it client_lab_1_dspwpcv2_container ./script.sh

echo "[+] Ip victima: $ip_address"


