#!/bin/bash

# Parse arguments
while getopts "n:" opt; do
  case $opt in
    n) n=$OPTARG ;;
    *) echo "Usage: $0 -n <number_of_users>"; exit 1 ;;
  esac
done

# Validate input
if [[ -z "$n" || ! "$n" =~ ^[0-9]+$ ]]; then
  echo "Error: -n must be a positive integer."
  exit 1
fi
sudo docker run --name mydb -e POSTGRES_USER=user -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=mydb -p 5432:5432 -d postgres
sleep 5
sudo docker run -d -p 4580:4580 --network host  lovelylazuli/certificate-authority
sleep 5
sudo docker run -d -p 4510:4510 --network host  lovelylazuli/human-resources-simulator
sleep 5
sudo docker run -d -p 4530:4530 --network host  lovelylazuli/it-manager-simulator
sleep 5
sudo docker run -d -p 4590:4590 --network host  lovelylazuli/ssp-manager-simulator
sleep 5
sudo docker run -d  -p 4520:4520 --network host lovelylazuli/sensor-simulator
sleep 5
sudo docker run -d  -p 8501:8501 --network host lovelylazuli/behavior-modeler
sleep 5
8501

for ((i=1; i<=n; i++)); do
  sudo docker run -d  --network host  lovelylazuli/user-simulator
  # Sleep for 5 seconds every 20 iterations
  if (( i % 40 == 0 )); then
    echo "Sleeping for 5 seconds after iteration $i..."
    sleep 5
  fi
done
