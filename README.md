# 🚀 IntelliFlow - Distributed Multi-Agent System

<div align="center">

![IntelliFlow](https://img.shields.io/badge/IntelliFlow-v1.0.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-teal?style=for-the-badge&logo=fastapi)
![Descope](https://img.shields.io/badge/Descope-OAuth-purple?style=for-the-badge)
![Gemini](https://img.shields.io/ badge/Google-Gemini_1.5-blue?style=for-the-badge&logo=google)

**An intelligent multi-agent RAG system with secure agent-to-agent communication, powered by FREE Google Gemini and Descope OAuth**

[Getting Started](#-getting-started) •
[Architecture](#-architecture) •
[Features](#-features) •
[API Documentation](#-api-documentation)

</div>

---

## 📋 Overview

IntelliFlow is an **Agentic RAG System** built for the **Descope Hackathon - Theme 3: Email Summarization + Calendar Action**. The system features:

- **🧠 RAG-Powered Intelligence**: Semantic search across email history using Qdrant vector database
- **🤖 Agent A (Email Summarizer)**: Fetches and summarizes emails using FREE Google Gemini 1.5 Flash
- **📅 Agent B (Calendar Manager)**: Creates calendar events based on extracted action items
- **🎯 Orchestrator**: LangGraph/CrewAI workflow management for multi-agent coordination
- **🔐 Secure Communication**: OAuth-based token delegation via Descope Inbound Apps
- **✅ User Consent Flow**: Delegated authorization for calendar modifications

## 🎯 Use Case

```
┌─────────────────┐     Delegated Token      ┌─────────────────┐
│                 │   (email.read scope)     │                 │
│   Agent A       │ ◄─────────────────────── │   Descope       │
│   (Summarizer)  │                          │   OAuth Server  │
│                 │                          │                 │
└────────┬────────┘                          └────────┬────────┘
         │                                            │
         │ Extract action items                       │
         │ + Request calendar access                  │
         ▼                                            ▼
┌─────────────────┐     Scoped Token         ┌─────────────────┐
│                 │  (calendar.write scope)  │                 │
│   Agent B       │ ◄─────────────────────── │   User Consent  │
│   (Calendar)    │                          │   Flow          │
│                 │                          │                 │
└─────────────────┘                          └─────────────────┘
```

## ✨ Features

### 🔐 Security Features
- **Descope Inbound Apps**: OAuth 2.0 token generation for each agent
- **Scope Enforcement**: Granular permissions (`email.read`, `email.summarize`, `calendar.write`)
- **Token Delegation**: Agent A securely delegates access to Agent B
- **JWT Validation**: All tokens validated using Descope's JWKS

### 🧠 RAG (Retrieval-Augmented Generation)
- **Semantic Search**: Find similar past emails using Qdrant vector database
- **Hybrid Retrieval**: Dense (semantic) + Sparse (keyword) search
- **Context Building**: Enhanced summaries with historical email context
- **Query Expansion**: Multi-query generation for better recall
- **Reranking**: Cohere rerank for improved relevance

### 🤖 Agent Capabilities
- **Email Processing**: Gmail API integration with LangGraph workflows
- **AI Summarization**: FREE Google Gemini 1.5 Flash (1500 requests/day)
- **Smart Extraction**: Action items and deadline detection
- **Calendar Integration**: Automatic event creation from summaries
- **Workflow Orchestration**: LangGraph/CrewAI for complex agent coordination

### 🎨 Frontend Features
- **Modern UI**: Next.js 14 + shadcn/ui + Tailwind CSS
- **RAG-Powered Search**: Semantic email search interface
- **Agentic Chat**: Chat with agents in real-time
- **Real-time Updates**: WebSocket + TanStack Query for live data
- **User Consent**: Descope Flows for OAuth consent screens
- **Dashboard**: Unified view of emails, summaries, and calendar

## 🏗️ Architecture

```
intelliflow/
├── backend/
│   ├── shared/                    # Shared utilities, RAG, auth
│   ├── orchestrator/              # 🎯 LangGraph/CrewAI workflow manager  
│   ├── agent-a-summarizer/        # 📧 Email intelligence agent
│   ├── agent-b-calendar/          # 📅 Calendar management agent
│   ├── rag-service/               # 🧠 Dedicated RAG service
│   └── api-gateway/               # 🌐 Express.js API gateway
├── frontend/                      # 💻 Next.js 14 web app
├── infrastructure/                # 🏗️ Docker, K8s, monitoring
├── docs/                          # 📚 Documentation
└── scripts/                       # 🛠️ Setup & utility scripts
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Agents** | Python 3.10+, FastAPI, LangGraph |
| **LLM Provider** | 🆓 **Google Gemini 1.5 Flash** (FREE - 1500 req/day) |
| **Vector Database** | Qdrant (for RAG) |
| **Embeddings** | Voyage AI / OpenAI |
| **Auth & OAuth** | Descope SDK |
| **Database** | PostgreSQL + SQLAlchemy |
| **Caching & Queue** | Redis + Celery |
| **Orchestration** | LangGraph / CrewAI |
| **Frontend** | Next.js 14, React 18, TypeScript |
| **UI Components** | shadcn/ui, Tailwind CSS |
| **State Management** | Zustand + TanStack Query |
| **Real-time** | WebSocket (Socket.io) |
| **Infrastructure** | Docker, Docker Compose, Kubernetes |

## 🚀 Getting Started

### Prerequisites

- Python 3.10+ (Python 3.10.0 or higher)
- Node.js 18+
- Docker & Docker Compose
- **Descope Account** (free tier - no credit card)
- **🆓 Google Gemini API Key** (FREE - no credit card!)
- Google Cloud account (for Gmail & Calendar APIs)

### 1. Clone & Setup

```bash
git clone <repository-url>
cd intelliflow
cp .env.example .env
```

### 2. Get FREE API Keys

#### 🆓 Google Gemini (LLM - FREE!)
1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (no credit card required!)
4. Free tier: 1500 requests/day

#### Descope (Auth - FREE!)
1. Visit: https://www.descope.com/
2. Sign up for free account
3. Create a new project
4. Copy Project ID and Management Key

### 3. Configure Environment

Edit `.env` with your credentials:

```env
# Descope Configuration
DESCOPE_PROJECT_ID=your_project_id
DESCOPE_MANAGEMENT_KEY=your_management_key

# 🆓 Google Gemini API (FREE!)
GOOGLE_GEMINI_API_KEY=AIzaSy...your_key_here

# Google APIs (for Gmail & Calendar)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Qdrant Vector Database (Optional - for RAG)
QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=  # Leave empty for local development
```

### 4. Install Dependencies

```bash
# Backend (Python)
pip install -e backend/shared
cd backend/agent-a-summarizer && pip install -r requirements.txt
cd ../agent-b-calendar && pip install -r requirements.txt

# API Gateway (Node.js)
cd backend/api-gateway && npm install

# Frontend (Next.js)  
cd frontend && npm install
```

### 5. Setup Descope

```bash
make setup-descope
```

This script will:
- Create Inbound Apps for Agent A and Agent B
- Configure scopes: `email.read`, `calendar.write`, `calendar.read`
- Set up OAuth flows

### 4. Start Development

```bash
make dev
```

### 5. Access Services

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API Gateway | http://localhost:3001 |
| Agent A | http://localhost:8001 |
| Agent B | http://localhost:8002 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## 📖 API Documentation

### Agent A - Email Summarizer

```http
POST /api/v1/summarize
Authorization: Bearer <descope_token>
Content-Type: application/json

{
  "email_ids": ["msg_123", "msg_456"],
  "create_calendar_events": true
}
```

### Agent B - Calendar Manager

```http
POST /api/v1/calendar/events
Authorization: Bearer <delegated_token>
X-Scope: calendar.write
Content-Type: application/json

{
  "title": "Follow up with client",
  "description": "Extracted from email thread",
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T11:00:00Z"
}
```

## 🔒 Security Model

### Token Flow

1. **User Login**: User authenticates via Descope Flow
2. **Token Exchange**: Agent A requests scoped token for email access
3. **Delegation**: Agent A delegates calendar scope to Agent B
4. **Scope Enforcement**: Agent B validates scopes before action

### Scope Definitions

| Scope | Description | Agent |
|-------|-------------|-------|
| `email.read` | Read user's email threads | Agent A |
| `email.summarize` | Generate AI summaries | Agent A |
| `calendar.read` | Read calendar events | Agent B |
| `calendar.write` | Create/modify events | Agent B |

## 🧪 Testing

```bash
# Run all tests
make test

# Unit tests only
make test-unit

# Integration tests
make test-integration

# End-to-end tests
make test-e2e
```

## 📦 Deployment

### Docker Compose (Production)

```bash
make build
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f infrastructure/kubernetes/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for the Descope Hackathon**

</div>
