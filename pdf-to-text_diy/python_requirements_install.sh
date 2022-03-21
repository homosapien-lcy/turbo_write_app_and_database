pip install numpy
pip install nltk
python -c 'import nltk;nltk.download("cmudict")'
python -c 'import nltk;nltk.download("stopwords")'
pip install inflect
pip install pathos
pip install flask
pip install pyspellchecker
conda install fasttext
conda install -c conda-forge faiss

sudo apt-get update
sudo apt-get install unzip
sudo apt-get install make
sudo apt-get install g++
wget https://github.com/facebookresearch/fastText/archive/v0.9.2.zip
sleep 5
unzip v0.9.2.zip
cd fastText-0.9.2/
make
cd ..
