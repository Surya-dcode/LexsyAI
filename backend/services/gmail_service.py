# backend/services/email_service.py

from services.vector_service import add_text_to_vectorstore
from datetime import datetime

def ingest_sample_emails(client_id: int):
    """Ingest sample emails for demo purposes"""
    
    sample_emails = [
        {
            'subject': 'Contract Review Request',
            'sender': 'client@example.com',
            'recipient': 'legal@lexsy.com', 
            'body': 'Hi, please review the attached service agreement. We need this completed by end of week.',
            'date_sent': '2025-07-20'
        },
        {
            'subject': 'Re: Contract Review Request',
            'sender': 'legal@lexsy.com',
            'recipient': 'client@example.com',
            'body': 'Thanks for sending this. I have reviewed the agreement and have some concerns about the liability clauses in section 4.',
            'date_sent': '2025-07-21'
        },
        {
            'subject': 'Compliance Question',
            'sender': 'client@example.com', 
            'recipient': 'legal@lexsy.com',
            'body': 'Do we need to file any additional paperwork for the new state registration?',
            'date_sent': '2025-07-22'
        }
    ]
    
    emails_processed = 0
    for email in sample_emails:
        try:
            metadata = {
                'source_type': 'email',
                'subject': email['subject'],
                'sender': email['sender'],
                'recipient': email['recipient'],
                'date_sent': email['date_sent']
            }
            
            add_text_to_vectorstore(client_id, email['body'], metadata)
            emails_processed += 1
            
        except Exception as e:
            print(f"Error processing sample email: {e}")
    
    return {
        'emails_processed': emails_processed,
        'message': f'Successfully ingested {emails_processed} sample emails'
    }
