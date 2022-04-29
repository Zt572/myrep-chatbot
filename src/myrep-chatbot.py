#----------------------------------------------------------------------------
# Created By  : Zt572
# Created Date: Apr 2022
# version ='1.0'
# Copyright Apr 2022
# ---------------------------------------------------------------------------
""" This script assembles the final chatbot. Handles connecting each separate piece together and
ensures that data is successfully transferred from module to module. The parts of the chatbot to 
assemble can be found in the chatbotparts subdirectory along with their dependencies."""
# ---------------------------------------------------------------------------
from chatbotparts import prog1, prog2, prog3ui, prog5logger
# ---------------------------------------------------------------------------
import sys
import subprocess
# ---------------------------------------------------------------------------

def main():
    # First, determine the district to obtain information from and extract info from the webpage
    district_name = input("Please enter the name of the district you would like information on: ")
    prog1.extract_info_93(district_name, update_info=True, pickle_info=True)    # Extract info from website if possible; output location can be changed in config

    # Then run the UI for the chatbot, passing in the local data
    local_data = prog2.load_data('district93_local.pkl')
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ DISTRICT CHATBOT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    prog3ui.run_ui(local_data)


if __name__ == "__main__":
    try:
        # Check if any arguments are passed. If none are given, assume that the user wishes to run the chatbot
        if not len(sys.argv) > 1:
            main()
        else:   # Otherwise assume the the user wishes to retrieve chatbot statistics; pass the args to the logging module
            subprocess.call(['python', './chatbotparts/prog5logger.py'] + sys.argv[1:])
    except KeyboardInterrupt as ki:
        print("KeyboardInterrupt--terminating program.")
        exit(0)