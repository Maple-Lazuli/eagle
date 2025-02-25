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

for ((i=1; i<=n; i++)); do
  sudo docker run -d  --network host  lovelylazuli/user-simulator
  # Sleep for 5 seconds every 20 iterations
  if (( i % 40 == 0 )); then
    echo "Sleeping for 5 seconds after iteration $i..."
    sleep 5
  fi
done
