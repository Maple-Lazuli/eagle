rm -f public*
rm -f private*
sudo docker build . -f Dockerfile -t lovelylazuli/sensor-simulator
sudo docker push lovelylazuli/sensor-simulator