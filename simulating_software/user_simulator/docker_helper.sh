rm -f public*
rm -f private*
sudo docker build . -f Dockerfile -t lovelylazuli/user-simulator
sudo docker push lovelylazuli/user-simulator