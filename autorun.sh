#!/bin/sh
mkdir output
set -e
while true
do
inotifywait $1
./iron_farm_inspector.py $1 output
done
