bash compress_cur_folder.sh
sleep 1
line=$1'p'
address=$(sed -n $line id_to_ip_list)
scp title_abstract_collector.tar.gz root@$address:~
scp uncompress.sh root@$address:~
sleep 1
