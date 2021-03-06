# Turbo Write Web Application and Database
Turbo write (https://www.turbo-write-test.com/) is a web application to help non-native English speakers to write English papers. 

The web app allows the reader to:

1. Organize their thoughts using our guideline ![alt text](https://github.com/homosapien-lcy/turbo_write_app_and_database/blob/main/webapp_demo_images/Guideline_demo.png?raw=true)
2. Insert images into the paper using upload panel![alt text](https://github.com/homosapien-lcy/turbo_write_app_and_database/blob/main/webapp_demo_images/Image_demo.png?raw=true)
3. Search for example sentences similar to what they want to express using example search function![alt text](https://github.com/homosapien-lcy/turbo_write_app_and_database/blob/main/webapp_demo_images/Sentence_example_demo.png?raw=true)
4. Search for evidence supporting their hypothesis using evidence search function![alt text](https://github.com/homosapien-lcy/turbo_write_app_and_database/blob/main/webapp_demo_images/Evidence_demo.png?raw=true)
5. Search for papers to cite using citation search function![alt text](https://github.com/homosapien-lcy/turbo_write_app_and_database/blob/main/webapp_demo_images/Citation_demo.png?raw=true)
6. Type fast while avoiding typo using scientific phrase input method![alt text](https://github.com/homosapien-lcy/turbo_write_app_and_database/blob/main/webapp_demo_images/Input_method_demo.png?raw=true)

The web app has four databases:

1. An example sentence database for the example search function (based on Elasticsearch)
2. An evidence database for the evidence search function (based on Faiss similarity search)
3. A citation search function connected to NCBI academic database for the citation search function
4. A vocabulary database for the scientific phrase input method (based on MongoDB) 

![alt text](https://github.com/homosapien-lcy/turbo_write_app_and_database/blob/main/database_demo_images/database_diagram_1.png?raw=true)
![alt text](https://github.com/homosapien-lcy/turbo_write_app_and_database/blob/main/database_demo_images/database_diagram_2.png?raw=true)
![alt text](https://github.com/homosapien-lcy/turbo_write_app_and_database/blob/main/database_demo_images/database_usage_illustration.png?raw=true)

