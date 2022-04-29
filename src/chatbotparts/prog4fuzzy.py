#----------------------------------------------------------------------------
# Created By  : Zt572
# Created Date: Mar 2022
# version ='1.1'
# Copyright Mar 2022
# ---------------------------------------------------------------------------
""" Maps user intent/response to known queries using Levenshtein Distance. The 'TheFuzz'
module included in this project can be found here: https://github.com/seatgeek/thefuzz.
The additional dependency it requires, difflib.py, is included here, within the module itself.

Updated to provide possible suggestion to user if the confidence for a match is just short of the
required_confidence, allowing for more forgiving use."""
# ---------------------------------------------------------------------------
import json
from math import floor
# ---------------------------------------------------------------------------
from chatbotparts.thefuzz import process
from string import punctuation
# ---------------------------------------------------------------------------

'''Replaces certain words within the given response with the similar word used in the known queries; for example, 
the word "congressman" in the user response would be replaced with "representative" as that's the term used within
the known queries. '''
def replace_with_similar(response, synonym_dict):
    if synonym_dict is None:    # If no dictionary of synonyms is specified, use default.
        synonym_dict = {("congressman","congresswoman","rep"):"representative",
                        ("congressman's","congresswoman's","rep's"):"representative's",
                        ("kid", "kids") : "children",
                        ("office", "workplace") : "work",
                        ("job", "position") : "role",
                        ("reach", "talk", "speak", "call") : "contact",
                        ("telephone","cellphone") : "phone",
                        ("date of birth", "dob") : "birthday",
                        ("degree","degrees","college","colleges","university","universities") : "education",
                        ("past", "prior") : "former",
                        ("government","govt") : "public office",
                        ("all information", "all info") : "everything",
                        ("my") : "the", # Assume that phrases such as "my representative" mean "the representative"
                        ("they", "he", "she") : "the representative",   # Assume vague pronouns refer to the representative
                        ("their","his","hers") : "the representative's"} # Assume that any vague absolute pronoun refer to the representative
    try:
        every_synonym_list = synonym_dict.keys()
        edited_response = response.strip(punctuation) + " "   # Strip punctuation marks from beginning and end and prepare to scan through response to replace similar words
    except AttributeError as ae:  # If an AttributeError is thrown, then the given synonym_dict isn't a dictionary or response isn't a string
        print("Make sure that the provided parameters are the expected type: " + str(ae))
        exit(1)
    
    for synonym_list in every_synonym_list:    # for each list of synonyms in the dictionary of synonyms
        relevant_word = synonym_dict[synonym_list]  # Grab the word used in the known queries (to replace the synonyms with)

        if isinstance(synonym_list, str):   # If there is only one synonym for the given relevant word, avoid looping (it would iterate by each character instead)
            # To avoid replace parts of preexisting words (i.e. replacing the "he" in "the"), replace only the words surrounded by spaces
            edited_response = edited_response.replace(" " + synonym_list + " ", " " + relevant_word + " ")
        else:
            for synonym in synonym_list:
                # To avoid replace parts of preexisting words (i.e. replacing the "he" in "the"), replace only the words surrounded by spaces
                edited_response = edited_response.replace(" " + synonym + " ", " " + relevant_word + " ")   # Replace any synonyms found with the relevant word       
    return edited_response

'''Matches the user's response to the closest known query string and returns the cloest match along with a boolean
denoting whether or not the match was exact, assuming a match was found (True if the confidence met the required confidence, False if it was within
3% of the required confidence). In short, this method relies on the "TheFuzz" package for calculating the Levenshtein Distance 
between the user's response and each known query; this metric is then used to determine the best match. If no match meets the confidence ratio, 
None will be returned.

An optional confidence_ratio can be provided which specifies how strictly the user response must match a known query 
in order to return a proper match. Additionally, one can provide a dictionary of synonyms to use instead of the default
(potentially useful if the known queries config is edited with new queries); dictionary entries should be in the form
of {tuple of synonym strings : intended word}'''
def map_intent(response, known_queries, required_confidence = 90, specified_synonyms = None):
    try:
        possible_queries = known_queries.keys()  # Grab all possible known queries
        
        # Ensure required_confidence is within expected bounds, notifying the user and correcting the value if it isn't
        if required_confidence < 0: 
            required_confidence = 0
            raise ValueError("required_confidence must be positive or zero. Defaulting to 0.")
        elif required_confidence > 100: 
            required_confidence = 100
            raise ValueError("required_confidence cannot exceed 100. Defaulting to 100.")
    except AttributeError as ae:  # If known_queries isn't a dictionary 
        print("Make sure that the provided parameters are the expected type: " + str(ae))
        exit(1)
    except TypeError as te:     # If required_confidence is not a number
        print("Make sure that required_confidence is an integer: " + str(te))
        exit(1)
    except ValueError as ve:    # No exiting needed as the values are corrected
        print(ve)

    # Find synonyms for words in the known queries and replace them with closer matching words to make the intent mapping more robust
    response = replace_with_similar(response, specified_synonyms)   
    # Calculate distance similarity ratio of response and each known query, then grab the 
    # best match and its ratio (100 being a perfect match)
    best_match = process.extractOne(response, possible_queries) 
    if(best_match[1] < required_confidence):    # if less than the required confidence, see if it's relatively close
        if(best_match[1] >= floor(required_confidence-(required_confidence*0.03))):   # If the best match is within 5%, give the suggestion
            return best_match[0], False
        # Otherwise there's not a good match
        return None, False  
    else:   # It's a confident match
        return best_match[0], True

# Primarily used for testing. This module is moreso meant to be imported for use in another script, e.g. prog3ui.py,
# where the map_intent is called directly
def main():
    # Initialize known queries from config.json early to avoid repeated loading later
    try:
        with open(r"../data/config.json", "r") as f:
            known_queries = json.load(f)    # Load dictionary of dictionaries from json. 
    except FileNotFoundError:
        print("~~Error: Config file not found; unable to load known queries. Default queries will be provided.~~\n")
        known_queries = {
            "tell me about my representative":"Personal Info",
            "representative live":"Contact Info:home address",
            "representative work":"Contact Info:columbia address",
            "contact my representative":"Contact Info",
            "representative's phone number":"Contact Info:phone",
            "representative's committees":"Committees",
            "representative's service in public office":"Service",
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
    # For standalone module testing:
    test_input = input("Enter your question here, q to quit: ")
    while test_input != 'q':
        print(map_intent(test_input, known_queries))
        print()
        test_input = input("Next question: ")

# Driver for main
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as ki:
        print("KeyboardInterrupt--terminating program.")
        exit(0)
