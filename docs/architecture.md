# IntelliFlow Architecture

## System Overview

IntelliFlow is a distributed multi-agent system demonstrating secure agent-to-agent communication for the Descope Hackathon. The system implements **Theme 3: Email Summarization + Calendar Action**.

## Architecture Diagram

```
                                    ┌─────────────────────────────────────────┐
                                    │              DESCOPE                     │
                                    │         (OAuth Provider)                 │
                                    │                                          │
                                    │  ┌─────────┐        ┌─────────┐         │
                                    │  │ Inbound │        │ Inbound │         │
                                    │  │  App A  │        │  App B  │         │
                                    │  └────┬────┘        └────┬────┘         │
                                    │       │                  │               │
                                    └───────┼──────────────────┼───────────────┘
                                            │                  │
                      ┌─────────────────────┼──────────────────┼─────────────────────┐
                      │                     │ Token Validation │                     │
                      │                     ▼                  ▼                     │
┌──────────┐    ┌─────┴─────┐    ┌─────────────────┐    ┌─────────────────┐        │
│          │    │           │    │                 │    │                 │        │
│  User    │───▶│  Frontend │───▶│   API Gateway   │───▶│   Agent A       │        │
│ Browser  │◀───│  Next.js  │◀───│   (Express)     │◀───│  Summarizer     │        │
│          │    │           │    │                 │    │   (FastAPI)     │        │
└──────────┘    └───────────┘    └────────┬────────┘    └────────┬────────┘        │
                                          │                      │                  │
                                          │                      │ Delegated Token  │
                                          │                      │ (calendar.write) │
                                          │                      ▼                  │
                                          │             ┌─────────────────┐        │
                                          │             │                 │        │
                                          └────────────▶│   Agent B       │        │
                                                        │   Calendar      │        │
                                                        │   (FastAPI)     │        │
                                                        └────────┬────────┘        │
                                                                 │                  │
                      ┌──────────────────────────────────────────┼──────────────────┘
                      │                                          │
                      ▼                                          ▼
               ┌─────────────┐                           ┌─────────────┐
               │  PostgreSQL │                           │    Redis    │
               │  Database   │                           │   (Cache)   │
               └─────────────┘                           └─────────────┘
```

## Component Details

### Frontend (Next.js 14)
- **Technology**: React 18, TypeScript, Tailwind CSS, shadcn/ui
- **Auth**: Descope React SDK for OAuth flows
- **State**: Zustand for local state, TanStack Query for server state
- **Purpose**: User interface for viewing emails, summaries, and calendar

### API Gateway (Express/TypeScript)
- **Purpose**: Central entry point for all API requests
- **Features**:
  - Token validation via Descope JWKS
  - Rate limiting
  - Request proxying to agents
  - CORS handling

### Agent A - Email Summarizer (Python/FastAPI)
- **Purpose**: Fetch and summarize emails
- **Framework**: LangGraph for agent workflows
- **LLM**: Anthropic Claude for AI summarization
- **Features**:
  - Gmail API integration
  - Action item extraction
  - Calendar event detection
  - Token delegation to Agent B

### Agent B - Calendar Manager (Python/FastAPI)
- **Purpose**: Manage calendar events
- **Features**:
  - Google Calendar API integration
  - Scope enforcement (calendar.read, calendar.write)
  - Delegation validation
  - Event CRUD operations

## Data Flow

### 1. Authentication Flow
```
User → Frontend → Descope Flow → Token Issued → Stored in Session
```

### 2. Email Summarization Flow
```
1. User requests email summary (Frontend)
2. Request goes to API Gateway with session token
3. API Gateway validates token, proxies to Agent A
4. Agent A:
   a. Validates token scopes (email.read, email.summarize)
   b. Fetches emails from Gmail API
   c. Generates summary using Claude
   d. Extracts action items and events
5. If calendar events detected:
   a. Agent A requests delegated token from Descope
   b. Delegated token has calendar.write scope
   c. Agent A calls Agent B with delegated token
6. Agent B:
   a. Validates delegated token
   b. Checks delegation source (must be Agent A)
   c. Enforces calendar.write scope
   d. Creates events via Google Calendar API
7. Response flows back to user
```

### 3. Token Delegation Flow
```
┌─────────┐          ┌─────────┐          ┌─────────┐
│ Agent A │          │ Descope │          │ Agent B │
└────┬────┘          └────┬────┘          └────┬────┘
     │                    │                    │
     │ Request Delegated  │                    │
     │ Token for Agent B  │                    │
     │ (calendar.write)   │                    │
     ├───────────────────▶│                    │
     │                    │                    │
     │ Delegated Token    │                    │
     │◀───────────────────┤                    │
     │                    │                    │
     │ Create Event Request                    │
     │ + Delegated Token                       │
     ├────────────────────────────────────────▶│
     │                    │                    │
     │                    │  Validate Token    │
     │                    │◀───────────────────┤
     │                    │                    │
     │                    │  Token Valid +     │
     │                    │  Correct Scopes    │
     │                    ├───────────────────▶│
     │                    │                    │
     │                    │                    │ Create Calendar
     │                    │                    │ Event
     │                    │                    │
     │ Event Created Response                  │
     │◀────────────────────────────────────────┤
     │                    │                    │
```

## Security Model

### OAuth Scopes
| Scope | Description | Used By |
|-------|-------------|---------|
| email.read | Read user's emails | Agent A |
| email.summarize | Generate AI summaries | Agent A |
| calendar.read | Read calendar events | Agent B |
| calendar.write | Create/modify events | Agent B |

### Token Types
1. **User Session Token**: Issued when user logs in, contains all permitted scopes
2. **Delegated Token**: Issued when Agent A needs to call Agent B, contains subset of scopes

### Delegation Validation
- Agent B validates that delegated tokens come from allowed sources
- Only Agent A is in the allowlist
- Tokens must have required scopes

## Database Schema

```
┌───────────────┐     ┌───────────────┐     ┌───────────────────┐
│    users      │     │    emails     │     │  email_summaries  │
├───────────────┤     ├───────────────┤     ├───────────────────┤
│ id (PK)       │──┐  │ id (PK)       │──┐  │ id (PK)           │
│ email         │  │  │ user_id (FK)  │◀─┘  │ email_id (FK)     │◀─┐
│ name          │  │  │ gmail_id      │     │ summary           │  │
│ descope_id    │  │  │ subject       │     │ key_points        │  │
│ google_conn   │  │  │ sender        │     │ action_items      │  │
│ preferences   │  │  │ body_text     │     │ detected_events   │  │
└───────────────┘  │  │ received_at   │─────│ sentiment         │  │
                   │  │ status        │     │ priority          │  │
┌───────────────┐  │  └───────────────┘     └───────────────────┘  │
│ user_tokens   │  │                                               │
├───────────────┤  │  ┌───────────────────┐                        │
│ id (PK)       │  │  │  calendar_events  │                        │
│ user_id (FK)  │◀─┘  ├───────────────────┤                        │
│ provider      │     │ id (PK)           │                        │
│ access_token  │     │ user_id (FK)      │◀───────────────────────┘
│ refresh_token │     │ google_event_id   │
│ expires_at    │     │ title             │
└───────────────┘     │ start_time        │
                      │ source            │
                      │ source_email_id   │
                      └───────────────────┘
```

## Deployment

### Docker Compose Services
1. **postgres**: PostgreSQL 15 database
2. **redis**: Redis 7 for caching and Celery
3. **agent-a**: Email Summarizer (port 8001)
4. **agent-b**: Calendar Manager (port 8002)
5. **api-gateway**: Express gateway (port 3001)
6. **frontend**: Next.js app (port 3000)
7. **celery-worker**: Background task processing

### Environment Variables
See `.env.example` for all required configuration.
