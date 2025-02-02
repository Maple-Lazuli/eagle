sudo docker build -t sensor .
sudo docker run -p 4590:4590 --network host  sensor
