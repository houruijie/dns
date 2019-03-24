#!/bin/sh

export SERVICE_IP=192.168.43.104
export SERVICE_PORT=5005

export REGISTER_URL=http://192.168.43.111:8080/executor/register

export FINISHED_URL=http://192.168.43.140:10001/task/worker
export RECEIVED_URL=http://192.168.43.140:10001/task/worker

export REDIS_IP=192.168.43.140
export REDIS_PORT=6379




