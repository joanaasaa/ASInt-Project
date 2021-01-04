# VQA By Joana
VQA By Joana was an app developed for the Internet Based Systems Architecture course.  
It is a simple YouTube-like app in which users can post videos, view them and post questions and answers about them.

## App components
### Databases
The app is has 4 different databases:
* **Users database** (```db_users.py```): This database stores all information regarding the app's users. The DB is made up of 3 tables:
    * Users table, which stores individual user information (username, name and email). All app users have an entry at this table with their information
    * Admins table, which stores the usernames of the users which are app administrators
    * User stats table, which, for each user, stores its statistics within the app. These include the number of views, videos posted, questions and answers made
* **Videos database** (```db_videos.py```):This database is made-up of a single table which stores all video information.
A video has the following information:
    * ID: Integer which is automatically generated and is used as a unique identifier for the video
    * URL: YouTube video URL
    * Description: Video description
    * Posted By: Username of the user who posted the video
    * Views: Total number of views the video has
    * Date: When the video was posted
* **QAs database** (```db_QAs.py```):This database is made-up of 2 tables, one for videos questions and another for their answers. 
A question has the following information:
    * ID: Integer which is automatically generated and is used as a unique identifier for the question
    * Question: A string with the actual question
    * Instant: Instant of the video (in seconds) for which the question is
    * Username: The user who made the question
    * Video ID: Video for which the question is
    * Date: When the question was made\
An answer has the following information:
    * ID: Integer which is automatically generated and is used as a unique identifier for the answer
    * Answer: A string with the actual answer
    * Username: The user who created the answer
    * Question ID: The question that is being answered
    * Date: When the answer was made
* **Logs database** (```db_logs.py```):This database is made-up of a single table which stores all log information. A log is considered to be a single communication/REST API request between 2 of the app's endpoints, which is considered an event. All of the possible communications are stored in an Enum called EventType, therefore, each log has an event-type. Each log also has:
    * Username: For the user responsible for teh communication between app endpoints
    * Date: When the communication happened
    * Origin IP address and port: Server who initiated the communication
    * Destination IP address and port: Location of teh server who has the destination endpoint
    * Content: Adds more information to the log beyond the event-type\
Important notes regarding the logs database:
    * When the origin address and port are '-', this means that the request was made by a user through the app's front-end webpages
    * Only POST requests have a username associated to them
    * When the content of the log is '-' it means that the event-type is descriptive enough to understand the request that was made


### Servers
There are 6 servers which make up the VQA By Joana app:
* **Proxy flask server** (```proxy.py```): The Proxy is a flask server which acts as the interface between the user and the backend of the app. It does this by providing 2 types of endpoints:
    * Endpoints to HTML interface webpages. These are directly access by the user and are the front-end of the app
    * REST API endpoints, which interact with the other app servers. These are accessed by the user through the HTML front-end webpages  
Since there's important information that has be consistent across databases, the Proxy is the one to make sure that all information adds up between DBs. For example, to create a new video (which has a user associated to it, the user who post it to the app), it's necessary to make sure that the username provided (as the user who posted the video) must exist in the user's database. This and similar checks are done by the Proxy
* **Users DB flask server** (```flask_users.py```): This flask server provides REST API endpoints which directly interact with the users database. These endpoints are accessed by the user through the Proxy
* **Videos DB flask server** (```flask_videos.py```): This flask server provides REST API endpoints which directly interact with the videos database. These endpoints are accessed by the user through the Proxy
* **QAs DB flask server** (```flask_videos.py```): This flask server provides REST API endpoints which directly interact with the videos' questions and answers database. These endpoints are accessed by the user through the Proxy
* **Logs DB flask server** (```flask_logs.py```): This flask server provides REST API endpoints which directly interact with the logs database. These endpoints are accessed by the user through the Proxy
* **Alternative users DB flask server** (```flask_users_alt.py```): This flask server is a copy of the users DB flask server which is meant to run on a different address or port. This server is meant to be used when the "original" users DB server is down as a way to implement fault tolerance in the app. The usage of this server is managed by the Proxy which has a thread (the ```servers_check``` function) that checks if the original server's address and port are open, using the Nmap tool. If the server's port is closed, the Proxy starts using the alternative server as the users DB server.

## Setting-up the app
The app is set-up to run locally. Nevertheless, the servers' IP addresses and ports can be changed in the ```config.yaml``` file.
Here are the steps to correctly run the app:
1. 
