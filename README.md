# Programming Assignment 6: Assembled Chatbot
myrep-chatbot.py brings together all previous components to form a fully functional chatbot for District 93. There are two major improvements over the past version of the previous parts: 1) there is now a simple config.py file which allows the user to specify the root directory for the chatbot, and 2) the chatbot now provides suggestions for queries that come close to a known one, further improving its intelligence. 

All the individual components were mostly unchanged. For information on the changes, see doc. 

## Usage
To run the chatbot, use the following:
```bash
python .\myrep-chatbot.py
```
To access recorded chat info, run the myrep-chatbot script with one of the mutually exclusive arguments from prog5:
```bash
python .\myrep-chatbot.py [-s] | [-sc session_num] | [-scs session_num]
```
The -s (--summary) command aggregates all the statistics of every recorded chat session and prints it to the command line; no additional argument needs to be specified. The -sc (--show_chat) command displays the actual chat recorded
for the specified session. Lastly, the -scs (--show_chat_summary) command displays the statistics of the specified session. Both -sc and -scs require an additional integer argument for specifying which chat to display/summarize.

## Navigation
The src directory contains the source code of myrep-chatbot as well as a subdirectory with all the source code used for the individual parts called 'chatbotparts'. For specific details on how these individual parts work, see their respective READMEs outside of this directory. The chatbotparts directory contains a new directory called 'config' which houses the two config files used for the chatbot: config.json contains the dictionary of known_queries, and config.py holds the path to the root directory of the project. These were included for user convenience and versatility.

The data directory contains the local copy of the representative's webpage data, both as a text file and as a pickled file. The data directory additionally contains: the chat_statistics csv file, which stores the statistics and text file name of each chat; and the chat_sessions directory, which contains the text files for each chat. Each chat text file holds a copy of the chat between the user and the chatbot as well as the statistics of that chat (for more info, see comments in source code).

The doc directory provides the information found here as well as some additional comments on the minor changes to the individual parts. A demo video for the chatbot is also provided along with the presentation slide I used
to present this project.

Lastly, the test directory contains an example log of the system with the current chat logs.

## Note on Deleting Text Files in Chat_Sessions
Since this chatbot relies on prog5logger.py, it does NOT automatically clean up chat_statistics.csv if you manually delete chat logs in the chat_sessions directory. For example, if chat session number 6's text file was deleted, the csv file will still contain information on session number 6 as if it weren't removed. So, **if you delete a chat's text file in chat_session, you must manually delete that chat's row in the csv file** or you'll get inaccurate results at best (or an unsuccessful run at worst if you try to specifically display stats or chat for a missing text file).
