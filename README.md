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
Current iteration

### API for looking up messages that contain a search phrase

Request: {'phrase' : <string to search form>
			'limit' : <max number of messages to return> }
Response: {'length' : <number of messages> 
			'messages' : [<list of messages in json format>]}


### API for returning messages that contain a given topic (topic id)

Request: {'topic_id' : <topic_id>
			'limit' : <max number of messages to return>}
Response: {'length' : <number of messages> 
			'messages' : [<list of messages in json format>]}

### API for returning top topics in messages containing a search phrase
(NEED TO RECONSIDER THIS)
Request: {'search_phrase' : <message_topic> 
			'limit' : <max number of messages to return> }
Response: {'length' : <number of messages> 
			'top_topics : [
				{	topic : <topic_name>,
					topic_id : <topic_id>
					message_count : <number_of_messages_in_this_topic>
				},
				{	topic : <topic2_name>,
					topic_id : <topic_id2>
					message_count : <number_of_messages_in_this_topic>
				}
				]
		    }

