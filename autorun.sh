#!/bin/sh
mkdir output
set -e
while true
do
inotifywait $1
sh -c "cd output && rm -- * || true"
./iron_farm_inspector.py $1 output
done
