#!/bin/bash
docker stop maquina_3_dspwpcv3_container 2&>1
docker rm maquina_3_dspwpcv3_container 2&>1
docker build -t maquina_3_dspwpcv3 /home/ubuntu/examen_dspwpcv3/Maquina_3 
docker run -p 56354:5000 -d --name maquina_3_dspwpcv3_container -it maquina_3_dspwpcv3