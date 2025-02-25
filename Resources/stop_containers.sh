sudo docker stop $(sudo docker ps -a -q)
sudo docker rm -f $(sudo docker ps -a -q)

