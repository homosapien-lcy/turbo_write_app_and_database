line=$1'p'
address=$(sed -n $line id_to_ip_list)
ssh root@$address