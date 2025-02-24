rm -f public*
rm -f private*
sudo docker build . -f Dockerfile -t lovelylazuli/it-manager-simulator
sudo docker push lovelylazuli/it-manager-simulator
