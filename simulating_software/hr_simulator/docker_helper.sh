sudo docker build -t hr .
sudo docker run -p 4510:4510 --network host  hr