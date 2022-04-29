#----------------------------------------------------------------------------
# Created By  : Zt572
# Created Date: Apr 2022
# version ='1.2'
# Copyright Apr 2022
# ---------------------------------------------------------------------------
""" Provides an interactable console-based UI for the chatbot. The PyDictionary
module included in this project was created by Pradipta Bora 2020--all rights reserved."""
# ---------------------------------------------------------------------------
import chatbotparts.prog2 as prog2
import json
# ---------------------------------------------------------------------------
from .config.definitions import ROOT_DIR
from chatbotparts.prog4fuzzy import map_intent
from chatbotparts.prog5logger import ChatSessionLogger
# ---------------------------------------------------------------------------

'''Extracts the info_type from the provided response. Handles stripping punctuation from the beginning and 
end of the response and utilizes prog4fuzzy's map_intent function to try and choose the closest known query from
the user's response. The known_queries dictionary and is provided in the config.json file within the data subdirectory.
Returns the extracted info type and a boolean representing whether or not the returned info type is a confident match rather than
a close suggestion. Returns None and False if no good match was found.'''
def extract_info_type(response, known_queries):
    # Check if response is a valid string
    try:
        response = response.lower() 
    except:
        print(f"~~Error: {response} was not a valid string!~~\n")
        return None, False, None

    # Find closest matching known query, if any
    response, is_confident = map_intent(response, known_queries, required_confidence=90)     

    try:    
        # Try to return the information associated with that known query. Also return the closest match in case we want to notify the user
        return known_queries[response], is_confident, response
    except KeyError:    # If the query isn't one of the known queries in the dictionary, there's no info
        return None, False, None
    except TypeError:   # A TypeError here will occur if known_queries isn't a dictionary
        print(f"~~Error: The provided known_queries is not a valid dictionary!~~")
        exit(1)


'''Apply a tab escape character before every line for prettier printing to console.'''
def tab_format(string):
    string = '\t' + string  # tab for first line
    return '\t'.join(string.splitlines(True))   # tabs for remaining lines

'''Run a simple while loop for user input, ending only when they input a 'yes' or 'no'. Returns True if yes,
False if no. Defaults to False if unexpected behavior occurs.'''
def get_yes_no(user_input):
    acceptable_responses = ['y', 'yes', 'yea', 'n', 'no', 'nay']
    try:
        while(user_input.lower() not in acceptable_responses):
            user_input = input("Response must be one of the following: " + str(acceptable_responses) + ", try again: ")
    except Exception as e:  # If an error occurs, gracefully continue by assuming that 'no' was inputted
        print("~~Error: Unexpected problem occurred when obtaining yes or no response: " + str(e))
        return False
    return (user_input.lower() in acceptable_responses[:3]) 


'''Runs the UI for the program, handling user input with regards to the info within local_data.'''
def run_ui(local_data):
    # Initialize known queries from config.json early to avoid repeated loading later
    try:
        config_path = ROOT_DIR + "/src/chatbotparts/config/config.json"
        with open(config_path, "r") as f:
            known_queries = json.load(f)    # Load dictionary of dictionaries from json. 
    except FileNotFoundError:
        print(f"~~Error: Config JSON file not found in {config_path}; unable to load known queries. Default queries will be provided.~~\n")
        known_queries = {
            "tell me about the representative":"Personal Info",
            "where does the representative live":"Contact Info:home address",
            "where does the representative work":"Contact Info:columbia address",
            "how do i contact the representative":"Contact Info",
            "what is the representative's phone number":"Contact Info:phone",
            "what committees is the representative on":"Committees",
            "what is the representative's service in public office":"Service",
            "tell me everything":"All" 
        }
    except Exception as e:
        print("~~JSON Loading Error: " + str(e) + ". Default queries will be provided.~~\n")
        known_queries = {
            "tell me about my representative":"Personal Info",
            "where does my representative live":"Contact Info:home address",
            "where does my representative work":"Contact Info:columbia address",
            "how do i contact my representative":"Contact Info",
            "what is my representative's phone number":"Contact Info:phone",
            "what committees is my representative on":"Committees",
            "what is my representative's service in public office":"Service",
            "tell me everything":"All" 
        }

    # Set up user response loop
    response = input("Welcome! Enter any questions about this representative and I'll try to answer. " +  
            "Type 'quit' or 'q' after any prompt to exit.\n")
    chat_output = None

    # Create ChatSessionLogger
    logger = ChatSessionLogger()    # Defaults to the data/chat_statistics.csv path, but a different csv can be specified

    while(response not in ('quit', 'Quit', 'q', 'Q')):
        found_relevant_answer = None  # Keep track of whether or not the chatbot found relevant info

        # Extract the info type requested (if one can be found) from the response
        info_type, is_confident, closest_query = extract_info_type(response.lower(), known_queries)

        # Using the parse_info method from prog2, retrieve the data associated with the info type from the local data
        output = prog2.parse_info(local_data, info_type)

        if(output is not None):     # If relevant info was found in the extracted info
            if is_confident:    # If the match was confident, a relevant answer will be given
                chat_output = f"You asked: '{response}', here's what I found:{tab_format(output)}\n"
                print(chat_output)
                found_relevant_answer = True
            else:   # Otherwise, ask the user if the suggested match is relevant
                chat_output = f"You asked: '{response}', here's my guess - '{closest_query}': {tab_format(output)}\n"
                print(chat_output)
                found_relevant_answer = get_yes_no(input("Did I answer correctly (y/n)? "))
                print() # Extra print for cleaner output to console
        else:
            chat_output = f"You asked: '{response}'; sorry, I don't know anything about that.\n"
            print(chat_output)
            found_relevant_answer = False

        # Log that question and answer if the user hasn't quit
        if response not in ('quit', 'Quit', 'q', 'Q'):
            logger.log_q_a((response, chat_output), is_helpful_answer=found_relevant_answer)

        response = input("What's your next question? ")

    # When done with the session, finalize it and finishing writing the chat info to the chat's own text file and the csv
    logger.finalize_session()

    print("\nTake care!")


def main():
    # Use load_data method from program 2 to obtain local copy of data from pickle file
    local_data = prog2.load_data('district93_local.pkl')

    # Call function to handle the ui loop
    run_ui(local_data)
    exit()

# Driver for main
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as ki:
        print("KeyboardInterrupt--terminating program.")
        exit(0)
