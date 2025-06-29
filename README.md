# zotero-downloader
 Simple tool to download your recently added files from Zotero web server.

 Disclaimer: The tool was vibe coded with the help of [Claude AI](https://claude.ai/). There might be inefficiencies and other bugs as I am not a programmer.

 Features
 * The tool downloads files added in the last *DAYS_BACK* days (you define how many days)
 * The tool tries to format the filenames based on the document title for easier navigation
 * Files are downloaded to a timestamped folder

 ## Requirements
 ### Necessary packages
 This tool is built using [Pyzotero](https://github.com/urschrei/pyzotero), which is required for the tool to run. 

### Zotero credentials
 In addition to finding out your Zotero user ID, you need to create a Zotero API key to interact with your Zotero library in the cloud. Instructions:
 * Go to https://www.zotero.org/settings/keys
 * Create a new private key with read access
 * Your user ID is shown on the same page

After you know your API key and user ID, enter these into the required .env file (see below). Do not share your API key with others.

(Note: this tool is only used with personal libraries, not group libraries)

### .env file
The tool reads your user ID and API key from an .env file located in the same folder as the python file. Here is the content that the .env file should have:

~~~
# Zotero API Configuration
ZOTERO_LIBRARY_ID=YOUR_ID_HERE
ZOTERO_LIBRARY_TYPE=user
ZOTERO_API_KEY=YOUR_KEY_HERE
~~~

Make your edits according to the instructions in the previous subsection ("Zotero credentials").
