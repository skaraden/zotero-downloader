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

### API key
 You need to create a Zotero API key to interact with your Zotero library in the cloud. Instructions:
 * Go to https://www.zotero.org/settings/keys
 * Create a new private key with read access
 * Your user ID is shown on the same page

After you know your API key and user ID, enter these into the .env file given in this repository. Do not share your API key with others.

(Note: this tool is only used with personal libraries, not group libraries)
