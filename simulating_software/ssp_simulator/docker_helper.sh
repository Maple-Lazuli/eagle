sudo docker build -t ssp .
sudo docker run -p 4520:4520 --network host  ssp
