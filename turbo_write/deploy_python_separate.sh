# force pull if needed
#git reset --hard HEAD
git pull
# stop and delete all jobs
pm2 stop all
pm2 delete all
# check and stop python process
cd ./server/pythonSubServer
if test -f python_server_process_id; then
    kill `cat python_server_process_id`
fi
# sleep for a while to wait until all memories are released before starting the python subserver again
echo 'sleep for 1 minutes to wait for memory release'
sleep 1m

# restart python subserver
python evidenceSearchPreloaded.py \
/root/turbo_write/pubmed_title_abstract_sentence_embedding/ \
flat pubmed_title_abstract \
/root/turbo_write/pubmed_title_abstract_idf_data_whole.pkl \
coverage \
/root/turbo_write/fastText-0.9.2/ &>> python_server.log &
echo $! > python_server_process_id
# back to turbo_write folder
cd ../..
# restart mongod and es
# restart them before the server to give it time to start properly
# start mongo db
sudo service mongod start
# install npm packages
bash install.sh
# overwrite the test server address
echo 'export const SERVER_ADDRESS = "https://turbo-write-test.com";' > ./client/src/components/constants/networkConstants.js
# restart client
cd ./client
npm run build
cp -r build/ /var/www/html/
cd ..
# restart server
cd ./server
sudo service nginx restart
# sleep for a while to wait for python data loading
echo 'sleep for 2 minutes to wait for data loading in python'
sleep 2m

# restart this process
pm2 start index.js --output ../server_log/output.log --error ../server_log/error.log --time

cd ..
echo "deployment has been completed"
