1. buy a domain name on godaddy
2. create droplet on digital ocean, additional options (Private networking, IPv6, etc.), no need to select any. But add ssh for easier login, if already has a public key, just copy with xclip (or pbcopy < ~/.ssh/id_rsa.pub on mac) and paste. Or select the existing ones.
3. now, we can log into the server through root@ipv4_address
4. go to godaddy and add the 3 name servers as shown here https://www.digitalocean.com/community/tutorials/how-to-point-to-digitalocean-nameservers-from-common-domain-registrars
5. check whether the DNS has been setup successfully by checking: https://www.godaddy.com/whois/ to see whether the 3 NS are up there
6. go to digital ocean and add domain and DNS record: droplet -> more -> add domain. Now you will start with 3 NS domains and 1 A domain. So you should add another A domain with www as subdomain prefix record since most people has the habit to add this prefix.
7. test the setup by log into the server through root@domain_name (root@turbo-write-test.com, for instance, may take a while after step 6)
8. install node.js 10 following the instructions here https://github.com/nodesource/distributions/blob/master/README.md, make sure to use v16
9. check version using: node -v; npm -v
10. add ssh key to bitbucket/github by following: https://confluence.atlassian.com/bitbucket/set-up-an-ssh-key-728138079.html#SetupanSSHkey-ssh2
11. git clone the codes from bitbucket/github
12. npm install all packages (now, you can use install.sh)
13. npm install -g pm2 (for program running management)
14. (necessary if you have python part in the server) install pip: sudo apt-get install python3-pip, upgrade pip: sudo pip3 install --upgrade pip
15. (necessary if you have python part in the server) pip install all packages (should used virtual-env or docker to make the versions local) (or using saved docker)
16. 14 and 15 are now included in the setup_computing.sh, but install anaconda first
17. install and start mongo (https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/), now, all included in install_mongo.sh (for specific version)
18. install elasticsearch, first may need to install default-jre and default-jdk (follow the java prerequisite here https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elastic-stack-on-ubuntu-18-04). Then, install elastic search as here (https://tecadmin.net/setup-elasticsearch-on-ubuntu/), but remember to change the verion of elasticsearch (don't configure yml as shown in that link, configure as shown in the next link). Now, all included in install_es.sh (for specific version of es 8.X)
19. Configure the yml file to be localhost: network.host: localhost (https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elastic-stack-on-ubuntu-18-04), disable xpack.security: xpack.security.enabled: false (https://stackoverflow.com/questions/35921195/curl-52-empty-reply-from-server-timeout-when-querying-elastiscsearch), start and enable service as shown: https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elastic-stack-on-ubuntu-18-04.
20. to have elastic search servie always running, do: sudo update-rc.d elasticsearch defaults 95 10 (https://www.elastic.co/guide/en/elasticsearch/reference/2.1/setup-service.html); sudo systemctl enable elasticsearch. The first command add it as a service, the second command starts it. Now you can just run start_es.sh
21. git clone the database setup script (which also include the database), construct the es database and test. The data base includes: sentence_database_constructor, vocabulary-database-processor, 
22. install nginx: sudo apt-get install nginx
23. setup nginx (/etc/nginx/sites-available/default):

---

```
server {

    root /var/www/html/build;

    index index.html index.nginx-debian.html;

    server_name turbo-write-test.com www.turbo-write-test.com;

    location / {
            try_files $uri $uri/ /index.html?/$request_uri;
    }

    # folder name should be the subroute
    location /api {
            # 5000 should be where the server is running
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
     }
}
```

---

24. set a larger max req size as shown here: https://www.keycdn.com/support/413-request-entity-too-large, if the request from client side can be large
25. check nginx status: systemctl status nginx
26. check the setup: sudo nginx -t
27. install and setup certbot as (installing certbot, obtaining an SSL certificate, verifying certbot auto-renewal): https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-14-04. when ask to Please choose whether or not to redirect HTTP traffic to HTTPS, removing HTTP access. Choose 2: Redirect - Make all requests redirect to secure HTTPS access. Choose this for new sites, or if you're confident your site works on HTTPS. You can undo this change by editing your web server's configuration. This will add new lines to /etc/nginx/sites-available/default. Now can be done by running install_certbot.sh: bash install_certbot.sh domain_name
28. ufw can be enabled as https://www.vultr.com/docs/how-to-configure-ufw-firewall-on-ubuntu-14-04 (make sure to enable access of 80 and ssh: sudo ufw allow ssh; sudo ufw allow 80/tcp; sudo ufw allow 443 (80 for unencrypted website access, 443 for encrypted). Or you will not be able to login from ssh!!!!!!!!!!). Now can be done by running install_and_setup_ufw.sh.
29. change the address (in networkConstants.js) in client from localhost to the url of your webpage (in this case http://localhost:5000 -> https://turbo-write-test.com)
29. move result/fasttext_model_dim_150_min_df_100/ to fasttext folder, move pubmed_title_abstract_sentence_embedding/ and pubmed_title_abstract_idf_data_whole.pkl to current folder (turbo_write), change the data paths in index.js
30. npm run build in the front end folder (client), if not successful, maybe not enough memory, need to run in another machine and upload
31. copy build from client to var: cp -r build/ /var/www/html/
32. pm2 start index.js start the server side (if need to restart: pm2 list to find the id and then pm2 restart id)
33. you can also do: pm2 stop all; pm2 delete all; pm2 start index.js
34. step 30-33 has been incorporated into deploy.sh. Just need to change echo 'export const SERVER_ADDRESS = "https://turbo-write-test.com";' in deploy.sh before that.
35. potential caveat: if run into bug "Mixed Content: The page at 'https://www.ewriteassist.com/' was loaded over HTTPS, but requested an insecure XMLHttpRequest endpoint 'http://ewriteassist.com:4000/api'. This request has been blocked; the content must be served over HTTPS." in the console, need to change http to https in root address
37. remove spellchecker in pythonSubServer/python_utils/sentenceEmbeddingUtils.py
38. change debug to False in the flask server
39. scp files to server, the followings are needed: result folder (for fasttext), vocabulary json files (for vocabulary), subject example json files (for example database), pubmed_title_abstract_idf_data_whole.pkl (for python server), pubmed_title_abstract_sentence_embedding folder (for python server, evidence search purporse)
40. test it in browser and done!!!!
41. mkl bug fix: add: export LD_PRELOAD=$CONDA_PREFIX/lib/libmkl_def.so:$CONDA_PREFIX/lib/libmkl_avx.s
    o:$CONDA_PREFIX/lib/libmkl_core.so:$CONDA_PREFIX/lib/libmkl_intel_lp64.so:$CONDA
_PREFIX/lib/libmkl_intel_thread.so:$CONDA_PREFIX/lib/libiomp5.so to .bashrc, with CONDA_PREFIX=path_to_conda
