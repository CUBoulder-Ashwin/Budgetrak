"""
Google Drive Tools for MCP

These tools allow Claude to interact with your Google Drive:
- List files in folders
- Download files
- Move/organize files
"""

import os
import io
from typing import List, Dict, Optional
from googleapiclient.http import MediaIoBaseDownload

from ..utils import get_drive_service


def list_drive_files(
    query: Optional[str] = None,
    folder_id: Optional[str] = None,
    max_results: int = 20
) -> List[Dict]:

    print(f"🔍 Searching Drive: query='{query}', folder='{folder_id}'")
    
    service = get_drive_service()
    
    # Build search query
    q_parts = []
    
    # Search by name if query provided
    if query:
        q_parts.append(f"name contains '{query}'")
    
    # Filter by folder if provided
    if folder_id:
        q_parts.append(f"'{folder_id}' in parents")
    
    # Only show PDFs (bank statements)
    q_parts.append("mimeType='application/pdf'")
    
    # Not in trash
    q_parts.append("trashed=false")
    
    q = " and ".join(q_parts)
    
    print(f"  Query: {q}")
    
    # Execute search
    results = service.files().list(
        q=q,
        pageSize=max_results,
        fields="files(id, name, mimeType, modifiedTime, size)",
        orderBy="modifiedTime desc"  # Newest first
    ).execute()
    
    files = results.get('files', [])
    print(f"✅ Found {len(files)} files")
    
    return files


def download_drive_file(file_id: str, destination: str) -> str:

    print(f"⬇️  Downloading file {file_id}...")
    
    service = get_drive_service()
    
    # Get file metadata
    file_metadata = service.files().get(fileId=file_id).execute()
    print(f"  File: {file_metadata['name']}")
    
    # Download file content
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"  Progress: {int(status.progress() * 100)}%")
    
    # Save to file
    with open(destination, 'wb') as f:
        f.write(fh.getvalue())
    
    print(f"✅ Downloaded to: {destination}")
    return destination


def move_drive_file(file_id: str, destination_folder_id: str) -> Dict:

    print(f"📁 Moving file {file_id} to folder {destination_folder_id}")
    
    service = get_drive_service()
    
    # Get current parents
    file_metadata = service.files().get(
        fileId=file_id,
        fields='parents, name'
    ).execute()
    
    print(f"  Moving: {file_metadata['name']}")
    
    # Remove from current parents and add to new parent
    previous_parents = ",".join(file_metadata.get('parents', []))
    
    updated_file = service.files().update(
        fileId=file_id,
        addParents=destination_folder_id,
        removeParents=previous_parents,
        fields='id, name, parents'
    ).execute()
    
    print(f"✅ Moved successfully")
    return updated_file


def create_drive_folder(name: str, parent_folder_id: Optional[str] = None) -> Dict:

    print(f"📁 Creating folder: {name}")
    
    service = get_drive_service()
    
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    
    folder = service.files().create(
        body=file_metadata,
        fields='id, name'
    ).execute()
    
    print(f"✅ Created folder: {folder['name']} (ID: {folder['id']})")
    return folder
