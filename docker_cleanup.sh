#!/usr/bin/bash

for container_id in $(docker ps --filter "status=exited" -q); do 
	docker rm $container_id; 
done;


for im_id in $(docker image ls --filter=dangling=true -q); do 
	docker image rm $im_id; 
done;
