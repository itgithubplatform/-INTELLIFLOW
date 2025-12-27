"""
Email Summarization Routes
==========================

API endpoints for email fetching and summarization.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status

from shared.auth import TokenClaims, validate_token, require_scope, Scope
from shared.utils import get_logger

from ..dependencies import get_gmail_service, get_llm_service, get_agent_b_client
from ...schemas.email import (
    EmailListRequest,
    EmailListResponse,
    SummarizeRequest,
    SummarizeResponse,
    SummaryResult,
    ActionItem,
    DetectedEvent,
)
from ...services.gmail_service import GmailService
from ...services.llm_service import LLMService
from ...services.agent_b_client import AgentBClient

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=EmailListResponse)
async def list_emails(
    max_results: int = 20,
    page_token: Optional[str] = None,
    query: Optional[str] = None,
    claims: TokenClaims = Depends(require_scope(Scope.EMAIL_READ)),
    gmail_service: GmailService = Depends(get_gmail_service),
):
    """
    List user's emails.
    
    Fetches emails from the user's Gmail account.
    Requires `email.read` scope.
    """
    try:
        emails = await gmail_service.list_emails(
            user_id=claims.sub,
            max_results=max_results,
            page_token=page_token,
            query=query
        )
        return EmailListResponse(
            emails=emails.get("emails", []),
            next_page_token=emails.get("next_page_token"),
            total_count=emails.get("total_count", 0)
        )
    except Exception as e:
        logger.error(f"Error listing emails: {e}", user_id=claims.sub)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emails: {str(e)}"
        )


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_emails(
    request: SummarizeRequest,
    background_tasks: BackgroundTasks,
    claims: TokenClaims = Depends(require_scope(Scope.EMAIL_READ, Scope.EMAIL_SUMMARIZE)),
    gmail_service: GmailService = Depends(get_gmail_service),
    llm_service: LLMService = Depends(get_llm_service),
    agent_b_client: AgentBClient = Depends(get_agent_b_client),
):
    """
    Summarize emails and optionally create calendar events.
    
    This endpoint:
    1. Fetches the specified emails
    2. Generates AI summaries using Claude
    3. Extracts action items and detects calendar events
    4. Optionally delegates to Agent B to create calendar events
    
    Requires `email.read` and `email.summarize` scopes.
    If `create_calendar_events` is true, requires delegation to Agent B
    with `calendar.write` scope.
    """
    logger.info(
        f"Summarize request received",
        user_id=claims.sub,
        email_count=len(request.email_ids),
        create_events=request.create_calendar_events
    )
    
    results = []
    all_detected_events = []
    
    try:
        # Fetch email content
        for email_id in request.email_ids:
            try:
                # Get email details
                email = await gmail_service.get_email(
                    user_id=claims.sub,
                    email_id=email_id
                )
                
                if not email:
                    results.append(SummaryResult(
                        email_id=email_id,
                        success=False,
                        error="Email not found"
                    ))
                    continue
                
                # Generate summary using LLM
                summary_result = await llm_service.summarize_email(
                    subject=email.get("subject", ""),
                    body=email.get("body", ""),
                    sender=email.get("sender", ""),
                    include_action_items=request.include_action_items,
                    include_events=request.detect_calendar_events
                )
                
                # Parse action items
                action_items = [
                    ActionItem(**item)
                    for item in summary_result.get("action_items", [])
                ]
                
                # Parse detected events
                detected_events = [
                    DetectedEvent(**event)
                    for event in summary_result.get("detected_events", [])
                ]
                all_detected_events.extend(detected_events)
                
                results.append(SummaryResult(
                    email_id=email_id,
                    success=True,
                    summary=summary_result.get("summary", ""),
                    key_points=summary_result.get("key_points", []),
                    action_items=action_items,
                    detected_events=detected_events,
                    sentiment=summary_result.get("sentiment"),
                    priority=summary_result.get("priority")
                ))
                
            except Exception as e:
                logger.error(f"Error summarizing email {email_id}: {e}")
                results.append(SummaryResult(
                    email_id=email_id,
                    success=False,
                    error=str(e)
                ))
        
        # Create calendar events if requested
        calendar_events_created = []
        if request.create_calendar_events and all_detected_events:
            try:
                # Create delegated token for Agent B
                delegated_token = await agent_b_client.get_delegated_token(
                    user_claims=claims,
                    scopes=["calendar.write"]
                )
                
                # Send events to Agent B
                for event in all_detected_events:
                    created_event = await agent_b_client.create_event(
                        token=delegated_token,
                        event_data=event.model_dump()
                    )
                    if created_event:
                        calendar_events_created.append(created_event)
                        
            except Exception as e:
                logger.error(f"Error creating calendar events: {e}")
                # Don't fail the entire request, just log the error
        
        return SummarizeResponse(
            success=True,
            results=results,
            calendar_events_created=calendar_events_created,
            total_processed=len(results),
            successful_count=len([r for r in results if r.success])
        )
        
    except Exception as e:
        logger.error(f"Summarization failed: {e}", user_id=claims.sub)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}"
        )


@router.get("/{email_id}")
async def get_email_details(
    email_id: str,
    claims: TokenClaims = Depends(require_scope(Scope.EMAIL_READ)),
    gmail_service: GmailService = Depends(get_gmail_service),
):
    """
    Get details of a specific email.
    
    Returns full email content including body, attachments, and metadata.
    Requires `email.read` scope.
    """
    try:
        email = await gmail_service.get_email(
            user_id=claims.sub,
            email_id=email_id
        )
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        
        return email
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching email {email_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch email: {str(e)}"
        )
