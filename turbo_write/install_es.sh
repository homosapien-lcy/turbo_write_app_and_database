# install java
sudo apt update
sudo apt install default-jre
java -version
sudo apt install default-jdk
javac -version

# install es
sudo apt-get install apt-transport-https
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
add-apt-repository "deb https://artifacts.elastic.co/packages/8.x/apt stable main"
sudo apt-get update
sudo apt-get install elasticsearch
