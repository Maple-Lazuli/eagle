rm -f public*
rm -f private*
sudo docker build . -f Dockerfile -t lovelylazuli/certificate-authority
sudo docker push lovelylazuli/certificate-authority