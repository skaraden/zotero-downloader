"""
Zotero Recent Documents Downloader
Downloads documents from Zotero library that were added in the past DAYS_BACK days.
"""

import os
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from pyzotero import zotero

class ZoteroDownloader:
    def __init__(self, user_id: str, api_key: str, library_type: str = 'user'):
        """
        Initialize Zotero downloader.
        
        Args:
            user_id: Your Zotero user ID
            api_key: Your Zotero API key
            library_type: 'user' or 'group' (default: 'user')
        """
        self.zot = zotero.Zotero(user_id, library_type, api_key)
        self.user_id = user_id
        
    def get_recent_items(self, days: int) -> List[Dict[str, Any]]:
        """
        Get items added to library in the past n days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of Zotero items
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Keep parent items only (limited to recent ones by API if possible)
        # Note: Zotero API doesn't have a direct date filter, so we fetch and filter
        try:
            items = self.zot.items(limit=100, sort='dateAdded', direction='desc')
            
        except Exception as e:
            print(f"Error fetching items: {e}")
            return []
        
        recent_items = []
        seen_keys = []
        for item in items:      
            # Parse the dateAdded field
            date_added_str = item['data'].get('dateAdded', '')
            if date_added_str:
                try:
                    # Zotero uses ISO 8601 format: 2024-01-15T10:30:00Z
                    date_added = datetime.fromisoformat(date_added_str.replace('Z', '+00:00'))
                    # Convert to local time for comparison (removing timezone info)
                    date_added = date_added.replace(tzinfo=None)
                    
                    if date_added >= cutoff_date: 
                        # These are the items of interest. Only add parent items.
                        if 'parentItem' not in item['data']:
                            item_key = item['key']
                            if item_key not in seen_keys:
                                seen_keys.append(item_key)
                                recent_items.append(item)

                    else:
                        # Since items are sorted by dateAdded desc, we can break early
                        break
                except ValueError:
                    print(f"Could not parse date: {date_added_str}")
                    continue
        
        return recent_items
    
    def get_item_attachments(self, item_key: str) -> List[Dict[str, Any]]:
        """
        Get attachments for a specific item.
        
        Args:
            item_key: The key of the parent item
            
        Returns:
            List of attachment items
        """
        try:
            attachments = self.zot.children(item_key)

            # Filter for file attachments only
            file_attachments = [
                att for att in attachments 
                if att['data'].get('itemType') == 'attachment' and 
                att['data'].get('linkMode') in ['imported_file', 'imported_url']
            ]
            return file_attachments
        except Exception as e:
            print(f"Error getting attachments for item {item_key}: {e}")
            return []
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing/replacing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename safe for filesystem
        """
        import re
        
        # Remove or replace invalid characters for most filesystems
        # Invalid chars: < > : " | ? * \ /
        invalid_chars = r'[<>:"|?*\\/]'
        filename = re.sub(invalid_chars, '_', filename)
        
        # Remove multiple consecutive spaces and underscores
        filename = re.sub(r'[_\s]+', '_', filename)
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Limit length (keeping some buffer for extension)
        max_length = 200
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        # Ensure filename is not empty
        if not filename:
            filename = "untitled"
            
        return filename
    
    def get_file_extension(self, attachment) -> str:
        """
        Extract file extension from original attachment.
        
        Args:
            attachment: Original attachment
            
        Returns:
            File extension including the dot (e.g., '.pdf')
        """
        content_type = attachment['data'].get('contentType')
        
        # Content is pdf or URL.
        if "pdf" in content_type:
            ext = ".pdf"
        else:
            ext = ".html"

        return ext
    
    def generate_unique_filename(self, base_name: str, extension: str, download_dir: str) -> str:
        """
        Generate a unique filename if file already exists.
        
        Args:
            base_name: Base filename without extension
            extension: File extension
            download_dir: Target directory
            
        Returns:
            Unique filename
        """
        filename = base_name + extension
        file_path = os.path.join(download_dir, filename)
        
        if not os.path.exists(file_path):
            return filename
        
        # File exists, add counter
        counter = 1
        while True:
            filename = f"{base_name}_{counter}{extension}"
            file_path = os.path.join(download_dir, filename)
            if not os.path.exists(file_path):
                return filename
            counter += 1
    
    def download_attachment(self, attachment: Dict[str, Any], parent_item: Dict[str, Any], download_dir: str) -> bool:
        """
        Download a single attachment file with custom naming.
        
        Args:
            attachment: Attachment item data
            parent_item: Parent item data for naming
            download_dir: Directory to save files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            attachment_key = attachment['key']
            original_filename = attachment['data'].get('filename', f"attachment_{attachment_key}")
            
            # Get parent item title for naming
            parent_title = parent_item['data'].get('title', 'Untitled')
            
            # Sanitize the parent title for use as filename
            base_filename = self.sanitize_filename(parent_title)
            
            # Get file extension from original filename
            file_extension = self.get_file_extension(attachment)
            #file_extension = ".pdf" # Just default to .pdf
            
            # Create download directory if it doesn't exist
            Path(download_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename if needed
            final_filename = self.generate_unique_filename(base_filename, file_extension, download_dir)
            
            # Get the file content
            file_content = self.zot.file(attachment_key)
            
            # Save to file
            file_path = os.path.join(download_dir, final_filename)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            print(f"Downloaded: {final_filename} (original: {original_filename})")
            return True
            
        except Exception as e:
            print(f"Error downloading attachment {attachment.get('key', 'unknown')}: {e}")
            return False
    
    def download_recent_documents(self, days: int, download_dir: str = "zotero_downloads") -> None:
        """
        Main method to download all documents from recent items.
        
        Args:
            days: Number of days to look back
            download_dir: Directory to save downloaded files
        """
        print(f"Fetching items added in the past {days} days...")
        recent_items = self.get_recent_items(days)
        
        if not recent_items:
            print("No recent items found.")
            return
        
        print(f"Found {len(recent_items)} recent items.")
        
        total_downloads = 0
        successful_downloads = 0
        
        for item in recent_items:
            item_key = item['key']
            title = item['data'].get('title', 'Untitled')
            print(f"\nProcessing: {title}")
            
            # Get attachments for this item
            attachments = self.get_item_attachments(item_key)
            
            if not attachments:
                print(f"  No file attachments found.")
                continue
            
            print(f"  Found {len(attachments)} attachment(s)")
            
            # Download each attachment
            for attachment in attachments:
                total_downloads += 1
                if self.download_attachment(attachment, item, download_dir):
                    successful_downloads += 1
        
        print(f"\n=== Download Summary ===")
        print(f"Total attachments found: {total_downloads}")
        print(f"Successfully downloaded: {successful_downloads}")
        print(f"Failed downloads: {total_downloads - successful_downloads}")
        print(f"Files saved to: {os.path.abspath(download_dir)}")


def main():
    # Configuration - Replace with your actual credentials in the .env file
    load_dotenv()

    USER_ID = os.getenv('ZOTERO_LIBRARY_ID')
    API_KEY = os.getenv('ZOTERO_API_KEY')

    # Number of days to look back
    DAYS_BACK = int(input("Enter DAYS_BACK: "))
    
    # Download directory
    current_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    DOWNLOAD_DIR = "zotero_recent_downloads_" + current_timestamp
    
    # Validate configuration
    if not USER_ID or not API_KEY:
        print("Please update USER_ID and API_KEY with your Zotero credentials in the .env file.")
        print("\nTo get your credentials:")
        print("1. Go to https://www.zotero.org/settings/keys")
        print("2. Create a new private key with read access")
        print("3. Your user ID is shown on the same page")
        sys.exit(1)
    
    try:
        # Create downloader instance
        downloader = ZoteroDownloader(USER_ID, API_KEY)
        
        # Download recent documents
        downloader.download_recent_documents(DAYS_BACK, DOWNLOAD_DIR)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
