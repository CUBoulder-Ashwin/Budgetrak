"""
Google Authentication Utility

Handles OAuth2 authentication for Google Drive and Sheets APIs.
Supports both OAuth credentials (for personal use) and Service Accounts (for automation).
"""

import os
import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google API Scopes - what permissions we need
SCOPES = [
    'https://www.googleapis.com/auth/drive',  # Full Drive access
    'https://www.googleapis.com/auth/spreadsheets',  # Sheets read/write
]


class GoogleAuthManager:
    """
    Manages Google API authentication and service creation.
    
    This class handles:
    1. OAuth token generation and refresh
    2. Service account authentication (future)
    3. Creating Google API service objects (Drive, Sheets)
    """
    
    def __init__(self, credentials_path: str = "budgetrak_credentials.json"):
        """
        Initialize the authentication manager.
        
        Args:
            credentials_path: Path to OAuth credentials JSON file
        """
        self.credentials_path = credentials_path
        self.token_path = "token.pickle"
        self._creds: Optional[Credentials] = None
    
    def authenticate(self) -> Credentials:
        """
        Authenticate with Google APIs using OAuth2.
        
        This method:
        1. Checks if we have saved credentials
        2. Refreshes expired tokens
        3. Runs OAuth flow if needed (opens browser)
        4. Saves credentials for future use
        
        Returns:
            Google OAuth2 credentials object
        """
        # Check if we have saved credentials
        if os.path.exists(self.token_path):
            print("📂 Loading saved credentials...")
            with open(self.token_path, 'rb') as token:
                self._creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                print("🔄 Refreshing expired token...")
                self._creds.refresh(Request())
            else:
                print("🔐 Running OAuth flow (browser will open)...")
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        f"Please download OAuth credentials from Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                self._creds = flow.run_local_server(port=0)
            
            # Save credentials for next time
            print("💾 Saving credentials...")
            with open(self.token_path, 'wb') as token:
                pickle.dump(self._creds, token)
        
        print("✅ Authentication successful!")
        return self._creds
    
    def get_drive_service(self):
        """
        Create and return Google Drive API service.
        
        Returns:
            Google Drive API service object
        """
        if not self._creds:
            self.authenticate()
        
        return build('drive', 'v3', credentials=self._creds)
    
    def get_sheets_service(self):
        """
        Create and return Google Sheets API service.
        
        Returns:
            Google Sheets API service object
        """
        if not self._creds:
            self.authenticate()
        
        return build('sheets', 'v4', credentials=self._creds)


# Singleton instance for easy access
_auth_manager: Optional[GoogleAuthManager] = None


def get_auth_manager(credentials_path: str = "budgetrak_credentials.json") -> GoogleAuthManager:
    """
    Get or create the singleton GoogleAuthManager instance.
    
    Args:
        credentials_path: Path to OAuth credentials JSON
        
    Returns:
        GoogleAuthManager instance
    """
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = GoogleAuthManager(credentials_path)
    return _auth_manager


def get_drive_service():
    """
    Quick access to Google Drive service.
    
    Returns:
        Google Drive API service
    """
    return get_auth_manager().get_drive_service()


def get_sheets_service():
    """
    Quick access to Google Sheets service.
    
    Returns:
        Google Sheets API service
    """
    return get_auth_manager().get_sheets_service()
