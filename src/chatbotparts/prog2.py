#----------------------------------------------------------------------------
# Created By  : Zt572
# Created Date: Feb 2022
# version ='1.0'
# Copyright Feb 2022
# ---------------------------------------------------------------------------
""" Processes extracted html from prog1 and returns relevant info based on console input."""
# ---------------------------------------------------------------------------
import argparse
from distutils.log import info
import re
# ---------------------------------------------------------------------------
from .config.definitions import ROOT_DIR
from chatbotparts.infocontainer import infocontainer as ic
from pickle import load
# ---------------------------------------------------------------------------


def load_pickle(pickle_name):
    with open(ROOT_DIR + f"/data/{pickle_name}", 'rb') as f:
        return load(f)

def load_data(file_name, from_pickle = True):
    if from_pickle:
        try:
            return load_pickle(file_name)
        except FileNotFoundError:
            print(f"{file_name} could not be found in 'data'. Place the pickled file in 'data' and try again.")
            exit(1)
        except:
            print("distict93_local.pkl is inaccessible. Try again.")
            exit(1)
    else:   # Else, try and retrieve the data from a text file
        try:
            local_data = None
            with open(ROOT_DIR + f"/data/{file_name}", 'r') as f: 
                local_data = f.readlines()
            local_data = "".join(local_data)  # convert list to one large string
            return local_data
        except FileNotFoundError:
            print(f"{file_name} could not be found in 'data'. Place the text file in 'data' and try again.")
            exit(1)
        except:
            print("distict93_local.txt is inaccessible. Try again.")
            exit(1)

def parse_info(local_data, info_type):
    # Once the data is retrieved, set up InformationContainers with the appropriate sections of data
    contactInfoContainer = None
    personalInfoContainer = None

    # Obtain start and end point of contact information. If an exception occurs, just pass all of the data to
    # the container's constructor as a failsafe
    try:
        info_start = re.search("barheader", local_data).start() 
        info_end = re.search("Personal Information", local_data).start()
        contactInfoContainer = ic.ContactInfoContainer(local_data[info_start,info_end])
    except:
        contactInfoContainer = ic.ContactInfoContainer(local_data)
    
    # Obtain start and end point of personal information. If an exception occurs, just pass all of the data to
    # the container's constructor as a failsafe
    try:
        info_start = re.search("Personal Information", local_data).start() 
        info_end = re.search("Committee Assignments", local_data).start()
        personalInfoContainer = ic.PersonalInfoContainer(local_data[info_start,info_end])
    except:
        personalInfoContainer = ic.PersonalInfoContainer(local_data)

    # Obtain start of service in public office information. If an exception occurs, just pass all of the data to
    # the container's constructor as a failsafe
    try:
        info_start = re.search("Service In Public Office", local_data).start() 
        serviceInfoContainer = ic.ServiceInfoContainer(local_data[info_start:])
    except:
        serviceInfoContainer = ic.ServiceInfoContainer(local_data)

    # Lastly, set up a service container containing the district information
    try:
        info_start = re.search("District\ [0-9]+", local_data).start() 
        districtInfoContainer = ic.DistrictInfoContainer(local_data[info_start:])
    except:
        districtInfoContainer = ic.DistrictInfoContainer(local_data)


    # After the containers are set up, parse the type of information provided by the user; if it's something
    # expected, then provide the relevant information. Otherwise return a lack of info message
    try:
        user_request = info_type.lower()
        category = None
        subcategory = None

        # If it has a subcategory, parse it and the main category separately
        if ':' in user_request:
            category = user_request[:user_request.index(':')]   # Everything before the colon
            subcategory = user_request[user_request.index(':')+1:]  # Everything after the colon
        else:   # Consider it all the main category
            category = user_request
    except TypeError:
        print("The type provided is invalid. Make sure the input is a valid string.")
        exit(1)
    except IndexError:
        print("Could not split input after ':' due to invalid input. Try again.")
        exit(1)
    except AttributeError:  # If type is None, that means the query could not find relevant info, so pass it on
        return None

    except:
        print("Error occurred in parsing the provided type. Make sure it's in a valid string format.")
        exit(1)

    # Establish available categories (and subcategories) of information
    category_dict = {
        "contact info" : ['name','home address','columbia address','phone'],
        "personal info" : ['birthday', 'parents', 'education', 'children', 'former', 'religion'],
        "service" : ['service'],
        "district" : ['district name', 'region']
    }
    # Likewise, set up matching dictionary for InfoContainers
    ic_dict = {
        "contact info" : contactInfoContainer,
        "personal info" : personalInfoContainer,
        "service" : serviceInfoContainer,
        "district" : districtInfoContainer
    }

    # Comprehend the provided category to see if the value is available
    info_output = ''   

    if category=='all':     # If all information is requested, print out info from every InfoContainer
        current_categories = category_dict.keys()
        for key in current_categories:
            info_output += ic_dict[key].format_dict_info()
    elif category in category_dict: # If the category is specified and its one of the known ones 
        if subcategory is None: # if there is not subcategory, print all the category's info
            info_output = ic_dict[category].format_dict_info()
        elif subcategory in category_dict[category]:     # If there's a valid subcategory, print out its info
            info_output = ic_dict[category].search(subcategory)
        else:   # Else, the subcategory does not exist; return None
            info_output = None
    else:   # Else, the category does not exist; return None
        info_output = None

    return info_output


def main():
    # Adding functionality for name command line argument as well as other optional command line arguments
    parser = argparse.ArgumentParser(description='House of Representatives SC District 93 Chatbot Data Processor', epilog='', add_help=True, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--type', required=True,
        help="REQUIRED: the type of information to retrieve (e.g. 'Contact Information' or 'Personal Information:education')")
    parser.add_argument('-p', '--pickle', action=argparse.BooleanOptionalAction, default=True,
        help="retrieve html information from a pickle file in 'data' folder; if false, attempts to read \
                from a text file in 'data' called 'district93_local'")
    parser.add_argument('-f', '--file', action='store', type=str, default='district93_local.pkl',
        help="the file to input the data from; district93_local.pkl by default")
    args = parser.parse_args()

    # Retrieve data in one piece, whether pickled or .txt
    local_data = load_data(args.file)

    # Return information based on provided type argument
    return parse_info(local_data, args.type)

# Driver for main
if __name__ == "__main__":
    main()