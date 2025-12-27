"""
Gmail Service
=============

Integration with Gmail API for fetching and processing emails.
"""

import base64
from datetime import datetime
from typing import Any, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from shared.utils import get_logger
from shared.utils.exceptions import ExternalServiceError, NotFoundError

logger = get_logger(__name__)


class GmailService:
    """
    Service for interacting with Gmail API.
    
    Handles authentication, fetching emails, and parsing content.
    """
    
    def __init__(self):
        """Initialize Gmail service."""
        self._service_cache: dict[str, Any] = {}
    
    async def _get_service(self, user_id: str, access_token: str):
        """
        Get Gmail API service instance for a user.
        
        Args:
            user_id: User ID
            access_token: Google OAuth access token
            
        Returns:
            Gmail API service
        """
        cache_key = f"{user_id}_{access_token[:20]}"
        
        if cache_key not in self._service_cache:
            credentials = Credentials(token=access_token)
            self._service_cache[cache_key] = build(
                "gmail",
                "v1",
                credentials=credentials,
                cache_discovery=False
            )
        
        return self._service_cache[cache_key]
    
    async def list_emails(
        self,
        user_id: str,
        access_token: str = None,
        max_results: int = 20,
        page_token: Optional[str] = None,
        query: Optional[str] = None,
        include_spam_trash: bool = False
    ) -> dict[str, Any]:
        """
        List emails from user's Gmail account.
        
        Args:
            user_id: User ID
            access_token: Google OAuth access token
            max_results: Maximum number of emails to return
            page_token: Pagination token
            query: Gmail search query
            include_spam_trash: Include spam and trash
            
        Returns:
            Dictionary with emails and pagination info
        """
        # For demo purposes, return mock data if no access token
        if not access_token:
            return self._get_mock_emails(max_results)
        
        try:
            service = await self._get_service(user_id, access_token)
            
            # Build request parameters
            params = {
                "userId": "me",
                "maxResults": max_results,
                "includeSpamTrash": include_spam_trash
            }
            
            if page_token:
                params["pageToken"] = page_token
            if query:
                params["q"] = query
            
            # Fetch message list
            response = service.users().messages().list(**params).execute()
            
            messages = response.get("messages", [])
            emails = []
            
            # Fetch details for each message
            for msg in messages:
                email_data = await self._get_email_details(
                    service,
                    msg["id"],
                    format="metadata"
                )
                if email_data:
                    emails.append(email_data)
            
            return {
                "emails": emails,
                "next_page_token": response.get("nextPageToken"),
                "total_count": response.get("resultSizeEstimate", len(emails))
            }
            
        except Exception as e:
            logger.error(f"Error listing emails: {e}")
            raise ExternalServiceError(
                message=f"Failed to list emails: {str(e)}",
                service="gmail"
            )
    
    async def get_email(
        self,
        user_id: str,
        email_id: str,
        access_token: str = None
    ) -> Optional[dict[str, Any]]:
        """
        Get detailed email content.
        
        Args:
            user_id: User ID
            email_id: Gmail message ID
            access_token: Google OAuth access token
            
        Returns:
            Email details with full body content
        """
        # For demo purposes, return mock data if no access token
        if not access_token:
            return self._get_mock_email_detail(email_id)
        
        try:
            service = await self._get_service(user_id, access_token)
            return await self._get_email_details(
                service,
                email_id,
                format="full"
            )
            
        except Exception as e:
            logger.error(f"Error fetching email {email_id}: {e}")
            if "404" in str(e):
                raise NotFoundError(
                    message="Email not found",
                    resource_type="email",
                    resource_id=email_id
                )
            raise ExternalServiceError(
                message=f"Failed to fetch email: {str(e)}",
                service="gmail"
            )
    
    async def _get_email_details(
        self,
        service,
        message_id: str,
        format: str = "metadata"
    ) -> Optional[dict[str, Any]]:
        """
        Fetch email details from Gmail API.
        
        Args:
            service: Gmail API service
            message_id: Gmail message ID
            format: 'metadata' or 'full'
            
        Returns:
            Parsed email data
        """
        try:
            message = service.users().messages().get(
                userId="me",
                id=message_id,
                format=format
            ).execute()
            
            # Parse headers
            headers = {
                h["name"].lower(): h["value"]
                for h in message.get("payload", {}).get("headers", [])
            }
            
            # Parse body if full format
            body_text = ""
            body_html = ""
            
            if format == "full":
                body_data = self._extract_body(message.get("payload", {}))
                body_text = body_data.get("text", "")
                body_html = body_data.get("html", "")
            
            # Parse date
            received_at = None
            if "date" in headers:
                try:
                    from email.utils import parsedate_to_datetime
                    received_at = parsedate_to_datetime(headers["date"])
                except Exception:
                    pass
            
            return {
                "id": message_id,
                "thread_id": message.get("threadId"),
                "subject": headers.get("subject", "(No Subject)"),
                "sender": headers.get("from", ""),
                "sender_name": self._parse_sender_name(headers.get("from", "")),
                "recipients": self._parse_recipients(headers),
                "received_at": received_at,
                "snippet": message.get("snippet", ""),
                "body": body_text or body_html,
                "body_text": body_text,
                "body_html": body_html,
                "labels": message.get("labelIds", []),
                "is_unread": "UNREAD" in message.get("labelIds", []),
                "is_important": "IMPORTANT" in message.get("labelIds", [])
            }
            
        except Exception as e:
            logger.warning(f"Error parsing email {message_id}: {e}")
            return None
    
    def _extract_body(self, payload: dict) -> dict[str, str]:
        """Extract text and HTML body from email payload."""
        result = {"text": "", "html": ""}
        
        def extract_parts(parts):
            for part in parts:
                mime_type = part.get("mimeType", "")
                body = part.get("body", {})
                data = body.get("data", "")
                
                if data:
                    decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                    if mime_type == "text/plain":
                        result["text"] = decoded
                    elif mime_type == "text/html":
                        result["html"] = decoded
                
                # Handle nested parts
                if "parts" in part:
                    extract_parts(part["parts"])
        
        # Check if payload has direct body
        if payload.get("body", {}).get("data"):
            data = payload["body"]["data"]
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            mime_type = payload.get("mimeType", "text/plain")
            if mime_type == "text/plain":
                result["text"] = decoded
            else:
                result["html"] = decoded
        
        # Check for parts
        if "parts" in payload:
            extract_parts(payload["parts"])
        
        return result
    
    def _parse_sender_name(self, sender: str) -> str:
        """Extract sender name from email address string."""
        if "<" in sender:
            return sender.split("<")[0].strip().strip('"')
        return sender.split("@")[0]
    
    def _parse_recipients(self, headers: dict) -> list[str]:
        """Parse recipients from email headers."""
        recipients = []
        for field in ["to", "cc", "bcc"]:
            if field in headers:
                recipients.extend([
                    addr.strip()
                    for addr in headers[field].split(",")
                ])
        return recipients
    
    def _get_mock_emails(self, count: int = 10) -> dict[str, Any]:
        """Return mock email data for demo/testing."""
        mock_emails = [
            {
                "id": f"msg_{i}",
                "thread_id": f"thread_{i}",
                "subject": f"Meeting Request: Project Update - Week {i}",
                "sender": f"sender{i}@example.com",
                "sender_name": f"Sender {i}",
                "received_at": datetime.now().isoformat(),
                "snippet": f"Hi, I wanted to follow up on our discussion...",
                "labels": ["INBOX", "UNREAD"] if i % 2 == 0 else ["INBOX"],
                "is_unread": i % 2 == 0,
                "is_important": i % 3 == 0
            }
            for i in range(1, count + 1)
        ]
        
        return {
            "emails": mock_emails,
            "next_page_token": None,
            "total_count": len(mock_emails)
        }
    
    def _get_mock_email_detail(self, email_id: str) -> dict[str, Any]:
        """Return mock detailed email for demo/testing."""
        return {
            "id": email_id,
            "thread_id": f"thread_{email_id}",
            "subject": "Meeting Request: Q1 Planning Session",
            "sender": "manager@company.com",
            "sender_name": "John Manager",
            "recipients": ["you@company.com", "team@company.com"],
            "received_at": datetime.now().isoformat(),
            "snippet": "Hi team, I'd like to schedule our Q1 planning session...",
            "body": """Hi Team,

I'd like to schedule our Q1 planning session for next Tuesday at 2:00 PM.

Please come prepared to discuss:
1. Current project status
2. Goals for Q1
3. Resource requirements

Location: Conference Room A

Action Items:
- Review Q4 results before the meeting
- Prepare your team's objectives
- Submit budget requests by Friday

Let me know if this time works for everyone.

Best regards,
John Manager""",
            "body_text": "...",
            "body_html": "",
            "labels": ["INBOX", "IMPORTANT"],
            "is_unread": True,
            "is_important": True
        }
