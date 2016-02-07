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
  PRIMARY KEY (`quote_id`),
  UNIQUE KEY `quote_id_UNIQUE` (`quote_id`)
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

### API for returning top topics overall (by message count)
Request: {"limit" : <max number of topics to return> }


Response: {"name" : "Top Topics", 
      "children" : [
        { "name" : <topic>,  "size" : <num messages> },
        { "name" : <topic2>, "size" : <num messages> }
      ]
    }

