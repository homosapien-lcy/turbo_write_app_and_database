# force pull if needed
#git reset --hard HEAD
git pull
# stop and delete all jobs
pm2 stop all
pm2 delete all
# restart mongod and es
# restart them before the server to give it time to start properly
# start mongo db
sudo service mongod start
# restart elastic search
sudo update-rc.d elasticsearch defaults 95 10
# sleep for a while to wait until all memories are released before starting the python subserver again
echo 'sleep for 1 minutes to wait for memory release'
sleep 1m
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
# restart this process
pm2 start index.js --output ../server_log/output.log --error ../server_log/error.log --time

echo "deployment has been completed"