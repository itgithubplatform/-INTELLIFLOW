"""
LLM Service
===========

Integration with Anthropic Claude for email summarization.
"""

import json
import time
from typing import Any, Optional

import anthropic

from shared.config import settings
from shared.utils import get_logger
from shared.utils.exceptions import ExternalServiceError

logger = get_logger(__name__)


class LLMService:
    """
    Service for AI-powered email summarization using Claude.
    
    Handles prompt construction, API calls, and response parsing.
    """
    
    def __init__(self):
        """Initialize LLM service with Anthropic client."""
        self.client = anthropic.Anthropic(
            api_key=settings.anthropic.api_key
        )
        self.model = settings.anthropic.model
        self.max_tokens = settings.anthropic.max_tokens
    
    async def summarize_email(
        self,
        subject: str,
        body: str,
        sender: str,
        include_action_items: bool = True,
        include_events: bool = True
    ) -> dict[str, Any]:
        """
        Generate an AI summary of an email.
        
        Args:
            subject: Email subject
            body: Email body content
            sender: Sender's email/name
            include_action_items: Extract action items
            include_events: Detect calendar events
            
        Returns:
            Dictionary with summary, action items, and events
        """
        start_time = time.time()
        
        # Build the prompt
        prompt = self._build_summary_prompt(
            subject=subject,
            body=body,
            sender=sender,
            include_action_items=include_action_items,
            include_events=include_events
        )
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                system="""You are an intelligent email assistant that summarizes emails,
                extracts action items, and detects calendar events. Always respond with
                valid JSON matching the requested structure."""
            )
            
            # Parse response
            content = response.content[0].text
            result = self._parse_response(content)
            
            # Add metadata
            processing_time = int((time.time() - start_time) * 1000)
            result["tokens_used"] = response.usage.input_tokens + response.usage.output_tokens
            result["processing_time_ms"] = processing_time
            result["model_used"] = self.model
            
            logger.info(
                "Email summarized successfully",
                tokens_used=result["tokens_used"],
                processing_time_ms=processing_time
            )
            
            return result
            
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise ExternalServiceError(
                message=f"LLM service error: {str(e)}",
                service="anthropic"
            )
        except Exception as e:
            logger.error(f"Error summarizing email: {e}")
            raise ExternalServiceError(
                message=f"Failed to summarize email: {str(e)}",
                service="llm"
            )
    
    def _build_summary_prompt(
        self,
        subject: str,
        body: str,
        sender: str,
        include_action_items: bool,
        include_events: bool
    ) -> str:
        """Build the prompt for email summarization."""
        
        extraction_instructions = []
        
        if include_action_items:
            extraction_instructions.append("""
            - "action_items": Array of action items with:
              - "title": Brief description of the action
              - "deadline": Date if mentioned (YYYY-MM-DD format), null if not
              - "priority": "low", "medium", "high", or "urgent"
              - "assignee": Person responsible if mentioned, null if not""")
        
        if include_events:
            extraction_instructions.append("""
            - "detected_events": Array of calendar events with:
              - "title": Event title
              - "description": Brief description
              - "date": Event date (YYYY-MM-DD format)
              - "time": Event time (HH:MM format, 24-hour)
              - "duration_minutes": Estimated duration (default 60)
              - "location": Location if mentioned
              - "attendees": Array of attendee emails/names
              - "confidence": 0.0-1.0 how confident you are this is a real event""")
        
        prompt = f"""Analyze the following email and provide a structured summary.

EMAIL DETAILS:
From: {sender}
Subject: {subject}

BODY:
{body[:4000]}  # Truncate very long emails

Please respond with a JSON object containing:
- "summary": A concise 2-3 sentence summary of the email
- "key_points": Array of 3-5 key points from the email
- "sentiment": "positive", "negative", or "neutral"
- "priority": "low", "medium", "high", or "urgent" based on content urgency
{"".join(extraction_instructions)}

IMPORTANT: Respond ONLY with valid JSON, no additional text."""

        return prompt
    
    def _parse_response(self, content: str) -> dict[str, Any]:
        """Parse LLM response into structured data."""
        try:
            # Try to extract JSON from the response
            content = content.strip()
            
            # Handle markdown code blocks
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])
            
            result = json.loads(content)
            
            # Ensure required fields
            if "summary" not in result:
                result["summary"] = "Unable to generate summary"
            if "key_points" not in result:
                result["key_points"] = []
            
            return result
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON")
            return {
                "summary": content[:500] if content else "Unable to generate summary",
                "key_points": [],
                "action_items": [],
                "detected_events": [],
                "sentiment": "neutral",
                "priority": "medium"
            }
    
    async def extract_action_items(self, text: str) -> list[dict[str, Any]]:
        """
        Extract action items from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of action items
        """
        prompt = f"""Extract all action items, tasks, and to-dos from the following text.
Return a JSON array where each item has:
- "title": Brief description
- "deadline": Date if mentioned (YYYY-MM-DD), null if not
- "priority": "low", "medium", "high", or "urgent"

Text:
{text[:3000]}

Respond with ONLY the JSON array."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error extracting action items: {e}")
            return []
    
    async def detect_events(self, text: str) -> list[dict[str, Any]]:
        """
        Detect calendar events from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected events
        """
        prompt = f"""Analyze the following text and detect any meeting requests,
appointments, or calendar events.

Return a JSON array where each event has:
- "title": Event title
- "date": Date (YYYY-MM-DD)
- "time": Time if mentioned (HH:MM, 24-hour)
- "duration_minutes": Estimated duration
- "location": Location if mentioned
- "confidence": 0.0-1.0 how confident you are

Text:
{text[:3000]}

Respond with ONLY the JSON array. Return [] if no events found."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error detecting events: {e}")
            return []
