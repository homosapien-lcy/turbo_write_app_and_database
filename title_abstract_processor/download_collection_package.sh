line=$1'p'
address=$(sed -n $line id_to_ip_list)
scp root@$address:~/data/* ./compressed_collection_files/