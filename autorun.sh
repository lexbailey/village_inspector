#!/bin/sh
mkdir output
set -e
while true
do
sh -c "cd output && rm -- * || true"
./iron_farm_inspector.py $1 output
inotifywait $1
done
