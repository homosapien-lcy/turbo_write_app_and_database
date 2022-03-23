# install
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python3-certbot-nginx

# certify
sudo certbot --nginx -d $1 -d www.$1

# dry run
sudo certbot renew --dry-run
