#!/bin/zsh

kafka.topics 0 --bootstrap-server localhost:9092 --create --topic MELLISHOPS
kafka.topics 0 --bootstrap-server localhost:9092 --create --topic VTEX
