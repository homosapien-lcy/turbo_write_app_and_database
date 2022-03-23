# install
sudo apt-get install ufw

# setup
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443

# enable and check status
sudo ufw enable
sudo ufw status
