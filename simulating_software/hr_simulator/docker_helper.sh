rm -f public*
rm -f private*
sudo docker build . -f Dockerfile -t lovelylazuli/human-resources-simulator
sudo docker push lovelylazuli/human-resources-simulator