#!/usr/bin/env python3
"""
Database Seeding Script
=======================

Seeds the database with sample data for development and testing.
"""

import os
import sys
from datetime import datetime, timedelta

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from sqlalchemy.orm import Session
    from shared.database import SessionLocal, init_db
    from shared.models import User, Email, EmailSummary, CalendarEvent
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure to install dependencies: pip install -e backend/shared")
    sys.exit(1)


def seed_users(db: Session) -> list:
    """Create sample users."""
    print("📝 Creating sample users...")
    
    users = [
        User(
            id="user_demo_1",
            email="demo@intelliflow.local",
            name="Demo User",
            descope_user_id="descope_demo_1",
            google_connected=True,
            google_email="demo@gmail.com",
            is_active=True,
            is_verified=True,
            preferences={"theme": "dark", "notifications": True}
        ),
        User(
            id="user_demo_2",
            email="test@intelliflow.local",
            name="Test User",
            descope_user_id="descope_demo_2",
            google_connected=False,
            is_active=True,
            is_verified=True,
        ),
    ]
    
    for user in users:
        existing = db.query(User).filter(User.id == user.id).first()
        if not existing:
            db.add(user)
            print(f"  ✅ Created user: {user.email}")
        else:
            print(f"  ⏩ User exists: {user.email}")
    
    db.commit()
    return users


def seed_emails(db: Session, user_id: str) -> list:
    """Create sample emails."""
    print("📧 Creating sample emails...")
    
    now = datetime.utcnow()
    
    emails = [
        Email(
            user_id=user_id,
            gmail_id="mock_msg_001",
            thread_id="mock_thread_001",
            subject="Q1 Planning Meeting - Please Confirm",
            sender="manager@company.com",
            sender_name="John Manager",
            snippet="Hi team, I'd like to schedule our Q1 planning session...",
            body_text="""Hi Team,

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
            received_at=now - timedelta(hours=2),
            is_unread=True,
            is_important=True,
            labels=["INBOX", "IMPORTANT", "UNREAD"],
            status="pending"
        ),
        Email(
            user_id=user_id,
            gmail_id="mock_msg_002",
            thread_id="mock_thread_002",
            subject="Project Deadline Reminder",
            sender="pm@company.com",
            sender_name="Sarah PM",
            snippet="Just a reminder that the project deliverables are due...",
            body_text="""Hi,

Just a reminder that the project deliverables are due by end of day Friday.

Please ensure you have:
- Completed all assigned tasks
- Updated the project tracker
- Submitted your time logs

Thanks,
Sarah""",
            received_at=now - timedelta(days=1),
            is_unread=False,
            is_important=True,
            labels=["INBOX", "IMPORTANT"],
            status="summarized"
        ),
    ]
    
    for email in emails:
        existing = db.query(Email).filter(Email.gmail_id == email.gmail_id).first()
        if not existing:
            db.add(email)
            print(f"  ✅ Created email: {email.subject[:40]}...")
        else:
            print(f"  ⏩ Email exists: {email.subject[:40]}...")
    
    db.commit()
    return emails


def seed_summaries(db: Session, emails: list):
    """Create sample email summaries."""
    print("📋 Creating sample summaries...")
    
    # Get the first email
    email = db.query(Email).filter(Email.gmail_id == "mock_msg_001").first()
    if not email:
        print("  ⚠️ No emails to summarize")
        return
    
    summary = EmailSummary(
        email_id=email.id,
        summary="Manager John is scheduling a Q1 planning meeting for next Tuesday at 2 PM in Conference Room A. Team members need to prepare by reviewing Q4 results and submitting budget requests by Friday.",
        key_points=[
            "Q1 planning session scheduled for next Tuesday 2 PM",
            "Location: Conference Room A",
            "Need to review Q4 results",
            "Budget requests due Friday"
        ],
        action_items=[
            {"title": "Review Q4 results", "deadline": None, "priority": "high"},
            {"title": "Prepare team objectives", "deadline": None, "priority": "high"},
            {"title": "Submit budget requests", "deadline": "Friday", "priority": "medium"}
        ],
        detected_events=[
            {
                "title": "Q1 Planning Meeting",
                "date": (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "time": "14:00",
                "duration_minutes": 60,
                "location": "Conference Room A",
                "attendees": [],
                "confidence": 0.95
            }
        ],
        sentiment="neutral",
        priority="high",
        model_used="claude-3-sonnet",
        tokens_used=450,
        processing_time_ms=1200
    )
    
    existing = db.query(EmailSummary).filter(EmailSummary.email_id == email.id).first()
    if not existing:
        db.add(summary)
        print(f"  ✅ Created summary for: {email.subject[:40]}...")
    else:
        print(f"  ⏩ Summary exists for: {email.subject[:40]}...")
    
    db.commit()


def seed_calendar_events(db: Session, user_id: str):
    """Create sample calendar events."""
    print("📅 Creating sample calendar events...")
    
    now = datetime.utcnow()
    
    events = [
        CalendarEvent(
            user_id=user_id,
            google_event_id="mock_event_001",
            title="Q1 Planning Meeting",
            description="Quarterly planning session for the team",
            location="Conference Room A",
            start_time=now + timedelta(days=2, hours=14),
            end_time=now + timedelta(days=2, hours=15),
            timezone="UTC",
            is_all_day=False,
            attendees=[
                {"email": "team@company.com", "name": "Team", "response_status": "needsAction"}
            ],
            source="email_summary",
            status="confirmed",
            is_synced=False,
            confidence_score=0.95,
        ),
        CalendarEvent(
            user_id=user_id,
            google_event_id="mock_event_002",
            title="Weekly Standup",
            description="Regular team sync",
            location="Zoom",
            start_time=now + timedelta(days=1, hours=9),
            end_time=now + timedelta(days=1, hours=9, minutes=30),
            timezone="UTC",
            is_all_day=False,
            source="user_created",
            status="confirmed",
            is_synced=True,
        ),
    ]
    
    for event in events:
        existing = db.query(CalendarEvent).filter(
            CalendarEvent.google_event_id == event.google_event_id
        ).first()
        if not existing:
            db.add(event)
            print(f"  ✅ Created event: {event.title}")
        else:
            print(f"  ⏩ Event exists: {event.title}")
    
    db.commit()


def main():
    """Main entry point."""
    print("\n🌱 Seeding IntelliFlow Database")
    print("=" * 50)
    
    # Initialize database tables
    print("\n📦 Initializing database...")
    init_db()
    print("  ✅ Database initialized")
    
    # Seed data
    with SessionLocal() as db:
        users = seed_users(db)
        user_id = users[0].id
        
        emails = seed_emails(db, user_id)
        seed_summaries(db, emails)
        seed_calendar_events(db, user_id)
    
    print("\n" + "=" * 50)
    print("✅ Database seeding complete!")
    print("\nYou can now:")
    print("1. Start the development server: make dev")
    print("2. Log in with demo@intelliflow.local")


if __name__ == "__main__":
    main()
