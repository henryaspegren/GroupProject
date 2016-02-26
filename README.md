# Group Project

# Database Schema

## Table: forum_messages
CREATE TABLE `forum_messages` (
  `message_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `time_stamp` text,
  `forum_name` text,
  `post` text,
  `cleaned_post` text,
  `sentiment` float DEFAULT NULL,
  PRIMARY KEY (`message_id`)
) ENGINE=InnoDB AUTO_INCREMENT=100001 DEFAULT CHARSET=latin1;


## Table: message_quotes 
CREATE TABLE `message_quotes` (
  `quote_id` varchar(45) NOT NULL,
  `message_id` int(11) NOT NULL,
  PRIMARY KEY (`message_id`,`quote_id`),
  CONSTRAINT `message_id` FOREIGN KEY (`message_id`) REFERENCES `forum_messages` (`message_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

## Table: quotes
CREATE TABLE `quotes` (
  `quote_id` varchar(45) NOT NULL,
  `quote_text` text NOT NULL,
  `quoted_message_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`quote_id`),
  UNIQUE KEY `quote_id_UNIQUE` (`quote_id`),
  KEY `message_id_idx` (`quoted_message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

## Table: message_topics
CREATE TABLE `message_topics` (
  `message_id` int(11) NOT NULL,
  `topic_id` int(11) NOT NULL,
  PRIMARY KEY (`message_id`,`topic_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

## Table: topics
CREATE TABLE `topics` (
  `topic_id` int(11) NOT NULL AUTO_INCREMENT,
  `topic` varchar(45) DEFAULT NULL,
  `message_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`topic_id`),
  UNIQUE KEY `topic_UNIQUE` (`topic`)
) ENGINE=InnoDB AUTO_INCREMENT=82 DEFAULT CHARSET=latin1;

## Table: users
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(45) DEFAULT NULL,
  `user_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_UNIQUE` (`user`)
) ENGINE=InnoDB AUTO_INCREMENT=82 DEFAULT CHARSET=latin1;


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

3.5)

The dependency pyner must be installed manually from inside the virtual environment. Download [pyner](https://github.com/dat/pyner) as a zip and then run 

$ python setup.py install

from inside the directory of the source files

4) when you want to leave the virtualenvironment 
just run 

$ deactivate

# NLP
divided into pre-processing, topic extraction and message processing modules. 

### Running Stanford NER as a standalone java module 
$   java -mx1000m -cp stanford-ner/stanford-ner.jar edu.stanford.nlp.ie.NERServer     -loadClassifier stanford-ner/classifiers/english.muc.7class.distsim.crf.ser.gz  -port 8070 -outputFormat inlineXML


When this server is running, make sure the socket is pointed to the correct hostname and port. Pass this into the extract_topic method in nlp.py

In order to do this you need to have a copy of the [stanford nlp distribution](http://stanfordnlp.github.io/CoreNLP/) as well as [pyner](https://github.com/dat/pyner) installed.

To install pyner execute the following 

$ cd lib/source/pyner

$ python setup.py install


# API
Current iteration

### API for looking up messages that contain a search phrase


They are returned in the order of increasing message ID. The limit restricts the number of messages returned (defaults to a limit of 10). The offset specifies the number of messages to skip (defaults to 0) to make it possible for multiple API calls to go through all the results.


Endpoint: /search_phrase/


Request: 
  
      {'phrase' : <string to search form>
			'limit' : <max number of messages to return> 
      'offset' : <number of messages to skip> }


Response: 

      {'length' : <number of messages> 
			'messages' : [{'message_id':self.message_id, 'user_id':self.user_id, 'forum_name': self.forum_name, 'post':self.cleaned_post, 'sentiment' : self.sentiment}, {'message_id':self.message_id, 'user_id':self.user_id, 'forum_name': self.forum_name, 'post':self.cleaned_post, 'sentiment' : self.sentiment}, ...]}

Example usage:

  ```{'phrase': "test", 'limit': 5, 'offset' : 0 }``` -> returns first 5 messages containing the string test
  ```{'phrase': "test", 'limit': 5, 'offset' : 5 }``` -> returns messages 5-10 containing the string test

### API for returning messages that contain a given topic (topic id)


They are returned in order of increasing message ID. The limit restricts the number of messages returned (defaults to a limit of 10). The offset specifes the number of messages to skip (defaults to 0) to make it possible for multiple API calls to go through all the results .


Endpoint: /search_topic/


Request: 

      {'topic_id' : <topic_id>
			'limit' : <max number of messages to return>
      'offset' : <number of messages to skip> }


Response: 

      {'length' : <number of messages> 
			'messages' : [<list of messages in json format>]}

Example usage:

  ```{'topic_id': 1, 'limit': 5, 'offset' : 0 }``` -> returns first 5 messages that are of topic 1
  ```{'topic_id': 1, 'limit': 5, 'offset' : 5 }``` -> returns messages 5-10 that are of topic 1

### API for returning top topics in messages containing a search phrase


They are returned in order of the number of messages per topic (containing the search phrase). The limit specifies the maximum number of topics that can be returned. The offset allows specifies the number of topics to skip. 


Endpoint: /top_topics_by_search_phrase/


Request: 

        {'search_phrase' : <message_topic> 
      			'limit' : <max number of messages to return> 
            'offset' : <number of messages to skip>}


Response:

        {'length' : <number of messages> 
      			'top_topics' : [
      				{	topic : <topic_name>,
      					topic_id : <topic_id>,
      					message_count : <number_of_messages_in_this_topic>,
                sentiment : <average_sentiment_of_messages_in_this_topic>
      				},
      				{	topic : <topic2_name>,
      					topic_id : <topic_id2>,
      					message_count : <number_of_messages_in_this_topic>,
                sentiment : <average_sentiment_of_messages_in_this_topic>
      				}
      				]
              'search_phrase_matches' : <number of messages matching the search phrase>
      		  }

Example Usage:

  ```{'search_phrase' : 'test', 'limit' : 5, 'offset' : 0 }``` -> top 5 (by message count) topics in messages containing the phrase "test"
  ```{'search_phrase': 'test', 'limit' : 5, 'offset' : 5}``` -> next 5 (5-10) top topics in messages containing the phrase "test"

### API for returning top topics overall (by message count)

Endpoint: /top_topics/

Request: 

      {"limit" : <max number of topics to return> }


Response: 

      {"name" : "Top Topics", 
        "children" : [
          { "name" : <topic>,  "size" : <num messages> },
          { "name" : <topic2>, "size" : <num messages> }
        ]
      }

### API for returning the top topics by number of messages in each forum. 


They are returned in order of the number of messages in each topic.


Endpoint : /top_topics_by_forum/

Request : 

        {"limit" : <max number of topics to return in each forum> }


Response : 

      {"data" : [
            [<forum name> [topic_1, topic_2, ...]],
            [<forum name> [topic_1, topic_2, ...]]
          ]
      }

      