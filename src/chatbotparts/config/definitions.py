"""Simple file used to provide paths and other definitions to the chatbot parts for convenience.
   These definitions may be modified to better suit the needs of the user, though the default values
   are expected by the modules in the project. Details can be found prior to each definition."""
import os

# Without any changes to the project structure, ROOT_DIR will be 'myrep-chatbot/'. All modules in this project
# which rely on this directory path expect said directory to contain a data subdirectory and a config 
# subdirectory at the very least. 
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
