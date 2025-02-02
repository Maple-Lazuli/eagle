sudo docker stop $(sudo docker ps -q)
sudo docker docker rmi -f $(sudo docker images -q)
