sudo docker build -t it .
sudo docker run -p 4530:4530 --network host  it