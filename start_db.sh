sudo docker stop $(sudo docker ps -a -q)
sudo docker rm -f $(sudo docker ps -a -q)

sudo docker run --name mydb -e POSTGRES_USER=user -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=mydb -p 5432:5432 -d postgres


