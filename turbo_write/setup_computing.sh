sudo apt-get update
sudo apt-get install unzip
sudo apt-get install screen
sudo apt-get install make
sudo apt-get install g++
sudo apt-get install libopenblas-dev
sudo apt-get install libomp-dev
sudo apt-get update;sudo apt-get -y upgrade; sudo apt-get install -y python3-pip
wget https://github.com/facebookresearch/fastText/archive/v0.9.2.zip
sleep 5
unzip v0.9.2.zip
cd fastText-0.9.2/
make
cd ..
bash python_requirements_install.sh
