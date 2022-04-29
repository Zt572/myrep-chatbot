#----------------------------------------------------------------------------
# Created By  : Zt572
# Created Date: Apr 2022
# version ='1.1'
# Copyright Apr 2022
# ---------------------------------------------------------------------------
""" Extracts data from the SC State House website and stores it locally, either as a text file
or a pickled file. Supports dynamic choice of output path."""
# ---------------------------------------------------------------------------
import os
import urllib.request as urlreq
# ---------------------------------------------------------------------------
from .config.definitions import ROOT_DIR
from pickle import dump
from urllib.error import URLError
# ---------------------------------------------------------------------------

def extract_info_93(district_name, update_info=True, pickle_info=True, outpath=None, verbose=False):
    # Build default output path from config file when the parameter isn't specified
    if outpath is None:
        outpath = os.path.join(ROOT_DIR, 'data')

    # Check the provided name to see if it's district 93. If it's not, exit early
    if district_name.lower() not in ['district93', '93', 'district 93', '93rd district']:
        print(f"Sorry, I cannot find information on a district named {district_name}." +
            " If you're still interested in District 93, though, try entering 'District 93' as the name.")
        exit()

    # Otherwise, continue on with the extracting 
    webpage = None
    if update_info:    # Try to request from the website to update the local data if possible
        url = "https://www.scstatehouse.gov/member.php?code=1433096420"
        try:
            webpage = urlreq.urlopen(url)  # Grab HTTP Response object
            html = webpage.read().decode("utf-8")   # Read bytes of HTML from the webpage and decode them (UTF-8 encoding scheme)
            with open(outpath + '/district_93_local.txt', 'w') as f:   # Write webpage HTML information to the local data text file
                f.write(html.strip())
        except URLError:    # If a client or server error code is returned, a URLError is thrown
            if webpage is None: # Print out relevant message depending on if an HTTP error code was received
                print("HTTP Request was unsuccessful. Defaulting to current local copy of webpage data.")
            else:
                print(f"HTTP Request was unsuccessful (error code: {webpage.status}). Defaulting to current local copy of webpage data.")
        except: # Catch other unexpected errors
            print("Request to the webpage was unsuccessful. Defaulting to current local copy of webpage data.")
    else:
        print("Skipping url request...")
    
    # Read in the data from the local copy
    # Note: read() is used instead of readline() since having all the file's contents as a single string allows for
    # broader searches to be done more easily. The downside is having to buffer the entire file in memory at once,
    # but the data is small enough in size for that not to cause unwanted behavior.
    local_text = ''
    with open(outpath + '/district_93_local.txt', 'r') as f:
        local_text = f.read().rstrip()   

    # Whittle down the file data to where the relevant information is (cleaning data)
    rel_info_start = local_text.find('<div class="mainwidepanel">')    # Index of when the relevant info begins
    rel_info_end = local_text.find('<!-- mainwidepanel -->')           # Index of when the relevant info ends
    local_text = local_text[rel_info_start:rel_info_end]

    if verbose:    # If specified, print out the modified webpage data to console as well as stats
        print("Trimmed Data: ")
        print(local_text)
        print("Stats (of Trimmed Data): ")
        print(f"\tNumber of current characters: {len(local_text)}")
        print(f"\tNumber of current words: {len(local_text.split())}")
        print(f"\tNumber of current lines: {len(local_text.splitlines())}")

        # Generic completion message
        print("Done! Output written to district93_local.txt.")

    # If pickling, dump the data into a pickle file before exit
    if pickle_info:
        with open(outpath + '/district93_local.pkl', 'wb') as f:
            dump(local_text, f)
        if verbose:
            print("Data has also been pickled to district93_local.pkl")
    print()

def main():
    district_name = input("Please enter the name of the district you would like information on: ")
    extract_info_93(district_name)

# Driver for main
if __name__ == "__main__":
    main()



