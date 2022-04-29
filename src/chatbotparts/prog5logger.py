#----------------------------------------------------------------------------
# Created By  : Zt572
# Created Date: Apr 2022
# version ='1.0'
# Copyright Apr 2022
# ---------------------------------------------------------------------------
"""  This script serves two main purposes: (1) it logs the statistics of chat session interactions across multiple sessions;
and (2) it provides convenient access to the logged information it recorded. The logging functionality is handled entirely by 
the included ChatSessionLogger class; to use the class in practice, simply import the ChatSessionLogger class from this script.
To access the recorded information, run this as a standalone script with the required arguments (check README and/or docs for more info).
"""
# ---------------------------------------------------------------------------
import argparse
import csv
import os
import pandas as pd
import sys
# ---------------------------------------------------------------------------
from datetime import datetime
from typing import Union
# ---------------------------------------------------------------------------

class ChatSessionLogger():
    """ A logger for logging a chat session between the user and the chatbot, keeping track of the chat's statistics 
    during the session. Handles writing chat information its own text file as well as recording that info to the specified csv file. 
    Use the log_q_a method to record queries and answers between the user and the chatbot, then use the finalize_session() method to 
    write the statistics to the local text file and update the specified csv with that log's info.

    Once the finalize_session() method is called, no further chat information and can logged (or written to the csv).
    """
    _start_time = None
    _chat_file_name = None
    _csv_path = None
    _chat_sessions_path = None
    _user_utterance_count = 0
    _system_utterance_count = 0
    _duration = None
    _finalized = False  # Tracks whether this logger's data has already been written to the provided .csv


    def __init__(self, csv_path='../data/chat_statistics.csv', text_path='../data/chat_sessions'):
        """ Creates a ChatSessionLogger for a given chat, initializing relevant variables. If no csv path is provided, the
        ChatSessionLogger will write the current session's information to a default location within the data subdirectory."""

        self._start_time = datetime.now()       # Set the time when the chat session starts
        # Create file name for chat session, 
        self._chat_file_name = str(self._start_time)[:-7].replace(" ","_")  # Exclude the decimal places for seconds and replacing space character with underline
        self._chat_file_name = self._chat_file_name.replace(":","-") + ".txt"   # Replace colons as they're invalid file name characters, and add extension
        self._csv_path = csv_path                                    # Set the csv path
        self._chat_sessions_path = text_path + "/" + self._chat_file_name  # Set the chat sessions folder path


    def _not_finalized(func):
        """ Decorator method used to check whether or not finalize_session() has been called already. If the session has been
        finalized, the decorated method cannot be used."""

        def method(self, *args, **kwargs):
            if self._finalized:
                raise Exception("ChatSessionLogger has already been finalized")
            else:
                func(self, *args, **kwargs)
        
        return method


    @_not_finalized
    def log_q_a(self, question_answer: Union[tuple, list], is_helpful_answer=True, add_newline=False):
        """ Creates a chat_session text file with the provided file name if it does not already exist and logs the user's questions and 
        the chatbot's answers. Also increments the utterance counts. question_answer must be a tuple or list with the first entry 
        being the user's question and the second entry being the chatbot's response. 
        
        This method assumes that all chatbot utterances were helpful by default. To signify that the chatbot found no relevant information for the question,
        set helpful_answer to False. Non-helpful answers will not contribute to the overall chatbot utterance count.
        Lastly, if add_newline is True, a newline character is added at the end of the question and answer."""

        # Create chat file if it does not exist already and write the provided question and answer to it
        try:
            with open(self._chat_sessions_path, "a") as chat_file:  # 'a' for appending. Creates file if it doesn't exist
                # Convert question and answer to a writeable string and add newline if specified
                question_answer_string = str(question_answer[0]) + " ~:~ " + str(question_answer[1])
                if add_newline:
                    chat_file.write(question_answer_string + "\n")
                else: chat_file.write(question_answer_string)

                # Increment statistics
                self._user_utterance_count += 1
                if is_helpful_answer:  # Only increment system response count if it had a helpful response (provides more meaningful stats)
                    self._system_utterance_count += 1
        except TypeError as te:
            print("The question_answer parameter must be a tuple or list: " + str(te))
            exit(1)
        except Exception as e:
            print("An error occurred when logging the previous question answer: " + str(e))
            exit(1)

   
    @_not_finalized
    def finalize_session(self):
        """ Finalizes the chat session, appending the current statistics to the end of the chat session text file and subsequently
        writing the chat session info to the specified csv file. Once the finalize_session() method is called, no further chat information and can logged and written to the csv.
        If the user immediately quit the session without asking at least one question then prevent the chat text file from being created and do not update
        the csv file."""  
        # Note: If this were written in C/C++, this would be akin to a destructor but with extra steps

        if self._user_utterance_count == 0: # If the user immediately quit, don't create a text file and update the csv with it
            self._finalized = True      # Mark this Logger as finalized
            return
        self._append_statistics()   # Append statistics to the end of the chat's own text file
        self._to_csv()              # Write this session's information to the specified csv
        self._finalized = True      # Mark this Logger as finalized


   
    def _append_statistics(self):
        """ Appends the current statistics to the end of the chat log in the following order: number of user utterances,
        number of system utterances, and the duration in seconds. """

        try:
            with open(self._chat_sessions_path, "a") as chat_file:  # 'a' for appending. Creates file if it doesn't exist
                chat_file.write(str(self._user_utterance_count) + "\n")
                chat_file.write(str(self._system_utterance_count) + "\n")

                # Calculate file session length
                self._duration = (datetime.now()-self._start_time).total_seconds()  # Calculate duration
                duration = str(round(self._duration, 2))          # Convert to string, round to reasonable amount of decimal places
                chat_file.write(duration)
        except Exception as e:
            print("An error occurred within _append_statistics: " + str(e))
            exit(1)


    def _to_csv(self):
        """ Writes the current chat text file's info and statistics to the .csv file specified in the constructor. 
        The information is written in the following order: session number, chat file name, number of user utterances, number of chat bot utterances, and duration in seconds."""

        # First, calculate and combine all relevant info into a single structure
        session_number = 1 
        try:
            with open(self._csv_path) as csv_file:
                session_number = sum(1 for row in csv_file)     # Determine session number by checking current count of rows in csv
        except FileNotFoundError:   
            pass    # If there is no csv file yet, keep the session number at 1 (its the first session recorded)
        
        # Capture all necessary chat info   
        chat_info = [(session_number, self._chat_file_name, self._user_utterance_count, self._system_utterance_count, round(self._duration, 2))]  

        # Then, using pandas DataFrames, we can effectively store and then write the individual log to the csv
        try:
            log_df = pd.DataFrame(chat_info, columns=["Session No.", "Chat File", "User Utt.", "Chatbot Utt.", "Duration"], )
            log_df.to_csv(self._csv_path, mode='a', header=not os.path.exists(self._csv_path), index=False)  # Only write header if the csv hasn't been made already
        except Exception as e:  # if question_answer isn't a tuple or list
            print("Error occurred when writing data to csv: " + str(e))
            exit(1)
# ---------------------------------------------------------------------------

def display_summary(chat_index: int = None, csv_path = '../data/chat_statistics.csv', chat_sessions_path = '../data/chat_sessions'):
    """Displays statistics for a specific chat session if the index integer is specified, or aggregate statistics for all sessions otherwise.
    Chat indexes start at 1. Another csv_path can be specified if desired; the default path corresponds to the default used in the ChatSessionLogger."""

    # To start, load CSV as a DataFrame
    try:
        chat_sessions_df = pd.read_csv(csv_path, delimiter=",")
    except FileNotFoundError:
        print("The csv file could not be found in the data subdirectory")
        exit(1)
    except Exception as e:
        print("The csv file could not be loaded when displaying summary: " + str(e))
        exit(1)

    # If chat_index is None, report aggregate statistics
    if chat_index is None:
        try:
            total_sessions = len(chat_sessions_df.index)
            total_user_utts = chat_sessions_df["User Utt."].sum()
            total_sys_utts = chat_sessions_df["Chatbot Utt."].sum()
            total_duration = round(chat_sessions_df["Duration"].sum(), 2)
        except Exception as e:
            print("Error occurred when aggregating statistics in the csv: " + str(e))
            exit(1)

        # Calculate success ratio (catching division by zero)
        try:
            success_ratio = round(float(total_sys_utts)/float(total_user_utts) * 100, 3)
        except ZeroDivisionError:  # If division by zero occurs, then chat log has user asking no questions. So set the success ratio to 0 as a default
            success_ratio = 0
        return (f"There are {total_sessions} chats to date with users asking {total_user_utts} times and "
                    f"system successfully answering {total_sys_utts} times ({success_ratio}% success rate). Total duration is {total_duration} seconds.")
    # Otherwise display the summary of the particular session
    else:
        try:
            last_session_index = chat_sessions_df.iloc[-1, 0]      # Grab the most recent session number for a boundary check
            if chat_index <= 0 or chat_index > last_session_index: # Check if a valid chat_index was used
                raise IndexError(f"Invalid chat_index provided. No chat with session number {chat_index} found within the specified csv file")
            else:
                # Load in the respective chat session's text file info by retrieving the file name from the csv
                chat_file_name = chat_sessions_df["Chat File"].iloc[chat_index-1]  # -1 is used as the session numbers start at 1, not 0
                chat_stats = [None, None, None]
                with open(chat_sessions_path + f'/{chat_file_name}') as chat_file:
                    # Since the statistics will be the last three lines of every chat text file, read those lines only
                    for inx, line in enumerate(chat_file.readlines()[-3:]):
                        chat_stats[inx] = line.strip()  # Strip newline character from stats
                    
                # Lastly, calculate success ratio (catching division by zero)
                try:
                    success_ratio = round(float(chat_stats[1])/float(chat_stats[0]) * 100, 3)
                except ZeroDivisionError:  # If division by zero occurs, then chat log has user asking no questions. So set the success ratio to 0 as a default
                    success_ratio = 0
                return (f"Chat {chat_index} has user asking {chat_stats[0]} times and system successfully answering {chat_stats[1]} times "
                            f"({success_ratio}% success rate). Total duration is {chat_stats[2]} seconds.")
        except IndexError as ie:
            print("Index Error occurred when displaying summary: " + str(ie))
            exit(1)
        except FileNotFoundError:
            print("No chat log text file with the name found in the csv could be found in /data/chat_sessions. "
                "Be sure to clear the matching row in the csv file if you manually remove specific chat logs.")
            exit(1)
        except TypeError as te:
            print(te)
            exit(1)

def _format_log(chat):
    """ Formats the raw chat info obtained from display_chat in order to print it out in a cleaner way. If an empty string
    is provided, return a notifying message."""
    output = ""
    query_num = 0  
    for line in chat:    # For each line in the chat
        line = line.split("~:~")        # Split line into its respective query and response
        try:
            output += f"\tQuery {str(query_num + 1)}: {line[0]} \n\t\t{line[1]}"
        except IndexError:  # If the current line doesn't have a "~:~", then assume it's part of the last answer
            output += f"\t\t {line[0]}"
            query_num -= 1  # Don't count a continuation as a new question/answer
        finally:
            query_num += 1
    if len(output) == 0:
        return "No chat to display within the specified log"
    else: return output



def display_chat(chat_index, csv_path = '../data/chat_statistics.csv', chat_sessions_path = '../data/chat_sessions'):
    """Displays the chat for a given chat session specified by the chat_index integer.
    Chat indexes start at 1. Another csv_path can be specified if desired; the default path corresponds to the default used in the ChatSessionLogger."""

    # To start, load CSV as a DataFrame
    try:
        chat_sessions_df = pd.read_csv(csv_path, delimiter=",")
    except FileNotFoundError:
        print("The csv file could not be found in the data subdirectory")
        exit(1)

    # Then check to see if the specified chat_index is valid (a non-negative, nonzero integer within boundaries)
    try:
        last_session_index = chat_sessions_df.iloc[-1, 0]      # Grab the most recent session number for a boundary check
        if chat_index <= 0 or chat_index > last_session_index: # Check if a valid chat_index was used
            raise IndexError(f"No chat with session number {chat_index} found within the specified csv file; there are only {last_session_index} total. "
                "Please choose a valid number.\n")
        else:
            # Load in the respective chat session's text file info by retrieving the file name from the csv
            chat_file_name = chat_sessions_df["Chat File"].iloc[chat_index-1]  # -1 is used as the session numbers start at 1, not 0
            with open(chat_sessions_path + f"/{chat_file_name}") as chat_file:
                # Since the statistics will be the last three lines of every chat text file, grab all but the last three lines and format it
                return chat_file.readlines()[:-3]
    except IndexError as ie:
        print(ie)
        exit(1)
    except FileNotFoundError:
        print("No chat log text file with the name found in the csv could be found in /data/chat_sessions. "
            "Be sure to clear the matching row in the csv file if you manually remove specific chat logs.\n")
        exit(1)


def main():
     # Adding functionality for command line arguments 
    parser = argparse.ArgumentParser(description='House of Representatives SC District 93 Chatbot Session Logger', epilog='', add_help=True, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    g = parser.add_mutually_exclusive_group()   # Create container for mutually exclusive commands
    g.add_argument('-s', '--summary', required=False, action="store_true",
        help="provides summary of statistics over all sessions")
    g.add_argument('-scs', '--show_chat_summary', required=False, type=int,
        help="provides summary of statistics for a given chat session indicated by the specified chat index")
    g.add_argument('-sc', '--show_chat', required=False, type=int,
        help="provides the actual chat recorded during the chat session indicated by the specified chat index")
    args = parser.parse_args()
    
    # Check if there were no arguments provided
    if not len(sys.argv) > 1:
        parser.error("No arguments provided")
        print("No arguments provided")
        exit(1)

    # Print specified output
    if args.summary:
        print(display_summary() + "\n")
    elif args.show_chat_summary is not None:
        print(display_summary(args.show_chat_summary)  + "\n")
    elif args.show_chat is not None:
        formatted_output = _format_log(display_chat(args.show_chat))
        print(f"Chat {args.show_chat} chat is: \n{formatted_output}")
    else:   # Else some extraneous argument(s)
        print("Unexpected argument(s). See documentation for usage")
        exit(1)

# Driver for main
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as ki:
        print("KeyboardInterrupt--terminating program.")
        exit(0)
