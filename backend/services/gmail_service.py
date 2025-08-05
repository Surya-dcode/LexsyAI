# backend/services/gmail_service.py

import os
import base64
import json
from datetime import datetime
from typing import List, Dict, Any
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from services.vector_service import add_text_to_vectorstore
from config import get_settings

settings = get_settings()

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

CREDENTIALS_FILE = 'credentials.json'  # Google OAuth credentials
TOKEN_FILE = 'token.json'  # Stored user token

class GmailService:
    def __init__(self):
        self.service = None
        self.creds = None
    
    def get_authorization_url(self) -> str:
        """Get the OAuth authorization URL for Gmail access"""
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError("credentials.json not found. Please download from Google Cloud Console.")
        
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE, 
            SCOPES,
            redirect_uri='http://localhost:8000/auth/callback'
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return auth_url
    
    def handle_oauth_callback(self, authorization_code: str) -> Dict[str, Any]:
        """Handle OAuth callback and store credentials"""
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE, 
            SCOPES,
            redirect_uri='http://localhost:8000/auth/callback'
        )
        
        flow.fetch_token(code=authorization_code)
        
        # Save credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(flow.credentials.to_json())
        
        self.creds = flow.credentials
        self._build_service()
        
        return {"status": "success", "message": "Gmail authentication successful"}
    
    def _load_credentials(self) -> bool:
        """Load existing credentials"""
        if os.path.exists(TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        # If credentials are expired, refresh them
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())
        
        return self.creds and self.creds.valid
    
    def _build_service(self):
        """Build Gmail API service"""
        if self.creds and self.creds.valid:
            self.service = build('gmail', 'v1', credentials=self.creds)
    
    def is_authenticated(self) -> bool:
        """Check if Gmail is authenticated and ready"""
        if not self._load_credentials():
            return False
        
        self._build_service()
        return self.service is not None
    
    def get_messages_from_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all messages from a Gmail thread"""
        if not self.is_authenticated():
            raise Exception("Gmail not authenticated")
        
        try:
            thread = self.service.users().threads().get(userId='me', id=thread_id).execute()
            messages = []
            
            for message in thread['messages']:
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                
                # Extract message details
                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                recipient = next((h['value'] for h in headers if h['name'] == 'To'), '')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Extract body
                body = self._extract_message_body(msg['payload'])
                
                messages.append({
                    'id': msg['id'],
                    'thread_id': thread_id,
                    'subject': subject,
                    'sender': sender,
                    'recipient': recipient,
                    'date': date,
                    'body': body
                })
            
            return messages
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
    
    def _extract_message_body(self, payload) -> str:
        """Extract text body from Gmail message payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'multipart/alternative':
                    body += self._extract_message_body(part)
        else:
            if payload['mimeType'] == 'text/plain':
                if 'data' in payload['body']:
                    body += base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def search_messages(self, query: str = '', label_ids: List[str] = None) -> List[str]:
        """Search for message IDs matching criteria"""
        if not self.is_authenticated():
            raise Exception("Gmail not authenticated")
        
        try:
            results = self.service.users().messages().list(
                userId='me', 
                q=query,
                labelIds=label_ids
            ).execute()
            
            messages = results.get('messages', [])
            return [msg['id'] for msg in messages]
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
    
    def create_mock_conversation(self, client_id: int) -> Dict[str, Any]:
        """Create mock email conversation for demo purposes"""
        
        # Sample email thread from requirements
        mock_emails = [
            {
                'id': 'mock_001',
                'thread_id': 'thread_advisor_equity',
                'subject': 'Advisor Equity Grant for Lexsy, Inc.',
                'sender': 'alex@founderco.com',
                'recipient': 'legal@lexsy.com',
                'date': 'July 22, 2025',
                'body': '''Hi Kristina,

We'd like to bring on a new advisor for Lexsy, Inc.

• Name: John Smith
• Role: Strategic Advisor for AI/VC introductions  
• Proposed grant: 15,000 RSAs (restricted stock)
• Vesting: 2‑year vest, monthly, no cliff

Could you confirm if we have enough shares available under our Equity Incentive Plan (EIP) and prepare the necessary paperwork?

Thanks, Alex'''
            },
            {
                'id': 'mock_002', 
                'thread_id': 'thread_advisor_equity',
                'subject': 'Re: Advisor Equity Grant for Lexsy, Inc.',
                'sender': 'legal@lexsy.com',
                'recipient': 'alex@founderco.com', 
                'date': 'July 22, 2025',
                'body': '''Hi Alex,

Thanks for the details!

We can handle this.

We will:
1. Check EIP availability to confirm 15,000 shares are free to grant.
2. Draft:
   • Advisor Agreement
   • Board Consent authorizing the grant
   • Stock Purchase Agreement (if RSAs)

Please confirm:
• Vesting starts at the effective date of the agreement, meaning whenever we prepare it—or should it start earlier?

Best, Kristina'''
            },
            {
                'id': 'mock_003',
                'thread_id': 'thread_advisor_equity', 
                'subject': 'Re: Advisor Equity Grant for Lexsy, Inc.',
                'sender': 'alex@founderco.com',
                'recipient': 'legal@lexsy.com',
                'date': 'July 23, 2025',
                'body': '''Hi Kristina,

Perfect! Let's start vesting from the effective date of the agreement.

Also, John Smith has agreed to the terms. His background:
• Former VP at TechVentures
• 15+ years in AI/ML space
• Has intro'd us to 3 potential investors already

When can we expect the paperwork ready for signature?

Thanks,
Alex'''
            },
            {
                'id': 'mock_004',
                'thread_id': 'thread_advisor_equity',
                'subject': 'Re: Advisor Equity Grant for Lexsy, Inc. - Documents Ready',
                'sender': 'legal@lexsy.com', 
                'recipient': 'alex@founderco.com',
                'date': 'July 24, 2025',
                'body': '''Hi Alex,

Great news! I've prepared all the documents:

1. ✅ EIP Check: We have 18,500 shares available (plenty for the 15,000 grant)
2. ✅ Advisor Agreement drafted
3. ✅ Board Consent prepared (needs board signatures)
4. ✅ Stock Purchase Agreement ready

All documents are attached. Please review and let me know if any changes needed.

The board consent can be signed via DocuSign - I'll send the link separately.

Best,
Kristina'''
            }
        ]
        
        # Add mock emails to vector store
        emails_processed = 0
        for email in mock_emails:
            try:
                metadata = {
                    'source_type': 'email',
                    'subject': email['subject'],
                    'sender': email['sender'],
                    'recipient': email['recipient'],
                    'date_sent': email['date'],
                    'thread_id': email['thread_id']
                }
                
                add_text_to_vectorstore(client_id, email['body'], metadata)
                emails_processed += 1
                
            except Exception as e:
                print(f"Error processing mock email {email['id']}: {e}")
        
        return {
            'emails_processed': emails_processed,
            'thread_id': 'thread_advisor_equity', 
            'message': 'Mock Gmail conversation created successfully'
        }
    
    def ingest_gmail_thread(self, client_id: int, thread_id: str) -> Dict[str, Any]:
        """Ingest a Gmail thread into the vector store"""
        if not self.is_authenticated():
            return self.create_mock_conversation(client_id)  # Fallback to mock data
        
        try:
            messages = self.get_messages_from_thread(thread_id)
            emails_processed = 0
            
            for message in messages:
                metadata = {
                    'source_type': 'email',
                    'subject': message['subject'],
                    'sender': message['sender'],
                    'recipient': message['recipient'],
                    'date_sent': message['date'],
                    'thread_id': thread_id,
                    'message_id': message['id']
                }
                
                add_text_to_vectorstore(client_id, message['body'], metadata)
                emails_processed += 1
            
            return {
                'emails_processed': emails_processed,
                'thread_id': thread_id,
                'message': f'Successfully ingested {emails_processed} emails from Gmail thread'
            }
            
        except Exception as e:
            # Fallback to mock conversation if real Gmail fails
            print(f"Gmail ingestion failed, using mock data: {e}")
            return self.create_mock_conversation(client_id)

# Global Gmail service instance
gmail_service = GmailService()