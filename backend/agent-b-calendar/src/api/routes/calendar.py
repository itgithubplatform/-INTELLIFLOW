"""
Calendar Routes
===============

API endpoints for calendar management.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status

from shared.auth import TokenClaims, validate_token, require_scope, Scope
from shared.utils import get_logger

from ..dependencies import get_calendar_service
from ...schemas.calendar import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventResponse,
    CalendarEventsListResponse,
)
from ...services.calendar_service import CalendarService
from ...core.scopes import CalendarScope, enforce_scope, validate_delegation
from ...core.config import agent_settings

router = APIRouter()
logger = get_logger(__name__)


@router.get("/events", response_model=CalendarEventsListResponse)
async def list_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    max_results: int = 50,
    claims: TokenClaims = Depends(validate_token),
    calendar_service: CalendarService = Depends(get_calendar_service),
    x_source_agent: Optional[str] = Header(default=None),
):
    """
    List calendar events.
    
    Requires `calendar.read` scope.
    Accepts delegated tokens from Agent A.
    """
    # Enforce scope
    enforce_scope(claims, CalendarScope.READ)
    
    # Validate delegation if from another agent
    if claims.delegation or x_source_agent:
        validate_delegation(claims, agent_settings.allowed_source_agents)
    
    logger.info(
        f"Listing calendar events",
        user_id=claims.sub,
        source_agent=x_source_agent
    )
    
    try:
        events = await calendar_service.list_events(
            user_id=claims.sub,
            start_date=start_date,
            end_date=end_date,
            max_results=max_results
        )
        
        return CalendarEventsListResponse(
            events=events,
            total_count=len(events)
        )
        
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list events: {str(e)}"
        )


@router.post("/events", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: CalendarEventCreate,
    claims: TokenClaims = Depends(validate_token),
    calendar_service: CalendarService = Depends(get_calendar_service),
    x_source_agent: Optional[str] = Header(default=None),
    x_delegation: Optional[str] = Header(default=None),
):
    """
    Create a calendar event.
    
    Requires `calendar.write` scope.
    Accepts delegated tokens from Agent A.
    
    When called by Agent A with a delegated token, the event is created
    on behalf of the user who originally authenticated.
    """
    # Enforce scope
    enforce_scope(claims, CalendarScope.WRITE)
    
    # Validate delegation if from another agent
    if claims.delegation or x_delegation == "true":
        validate_delegation(claims, agent_settings.allowed_source_agents)
        logger.info(
            f"Creating event via delegation from {x_source_agent}",
            user_id=claims.sub
        )
    
    logger.info(
        f"Creating calendar event",
        user_id=claims.sub,
        title=event.title,
        source_agent=x_source_agent
    )
    
    try:
        created_event = await calendar_service.create_event(
            user_id=claims.sub,
            event_data=event.model_dump()
        )
        
        return CalendarEventResponse(**created_event)
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )


@router.get("/events/{event_id}", response_model=CalendarEventResponse)
async def get_event(
    event_id: str,
    claims: TokenClaims = Depends(validate_token),
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """
    Get a specific calendar event.
    
    Requires `calendar.read` scope.
    """
    enforce_scope(claims, CalendarScope.READ)
    
    try:
        event = await calendar_service.get_event(
            user_id=claims.sub,
            event_id=event_id
        )
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        return CalendarEventResponse(**event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch event: {str(e)}"
        )


@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: str,
    event: CalendarEventUpdate,
    claims: TokenClaims = Depends(validate_token),
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """
    Update a calendar event.
    
    Requires `calendar.write` scope.
    """
    enforce_scope(claims, CalendarScope.WRITE)
    
    logger.info(f"Updating event {event_id}", user_id=claims.sub)
    
    try:
        updated_event = await calendar_service.update_event(
            user_id=claims.sub,
            event_id=event_id,
            event_data=event.model_dump(exclude_unset=True)
        )
        
        if not updated_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        return CalendarEventResponse(**updated_event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update event: {str(e)}"
        )


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    claims: TokenClaims = Depends(validate_token),
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    """
    Delete a calendar event.
    
    Requires `calendar.write` scope.
    """
    enforce_scope(claims, CalendarScope.WRITE)
    
    logger.info(f"Deleting event {event_id}", user_id=claims.sub)
    
    try:
        success = await calendar_service.delete_event(
            user_id=claims.sub,
            event_id=event_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete event: {str(e)}"
        )
