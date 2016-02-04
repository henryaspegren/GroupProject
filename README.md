# Group Project

# Database Schema

table: forum_messages
contains: message_id (int, PK, NN), user_id (int), time_stamp (string), forum_name (string), post (string), cleaned_post (string)

table: topics 
contains: topic_id (int), topic (string), message_count (int)

table: message_topics
contains: topic_id (int, FOREIGN KEY, PK), message_id (int, FOREIGN KEY, PK)

table: message_quotes
contains: quote_id (string, PK, Unique), message_id (int FOREIGN KEY, PK)

table: quotes
contains: quote_id (string, PK, Unique), quote_text (string, NOT NULL)

# Setup for Python portion
1) install pip and virtualenv. Pip allows you to install python
dependencies and virtualenv is a virtual environment manager that 
makes synchronizing across platforms easy.

2) create a virtual environment where the 
 python project can live

$ virtualenv virt
$ source virt/bin/activate

3) now install all the required dependencies (foolproof!)

$ pip install -r requirements.txt

4) when you want to leave the virtualenvironment 
just run 

$ deactivate

# NLP
divided into pre-processing, topic extraction and message processing modules. 

# API
Located in api.py. Uses JSON serialization and the format for requests and responses is specified in the google doc.

