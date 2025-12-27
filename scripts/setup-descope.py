#!/usr/bin/env python3
"""
Descope Setup Script
====================

Sets up Descope Inbound Apps for Agent A and Agent B.
Configures OAuth scopes and permissions.
"""

import os
import sys
import json
from typing import Optional

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)


class DescopeSetup:
    """Configure Descope for IntelliFlow agents."""
    
    def __init__(self, project_id: str, management_key: str):
        self.project_id = project_id
        self.management_key = management_key
        self.base_url = "https://api.descope.com/v1/mgmt"
        
    def _headers(self) -> dict:
        """Get auth headers."""
        return {
            "Authorization": f"Bearer {self.management_key}",
            "Content-Type": "application/json"
        }
    
    def create_inbound_app(
        self,
        app_id: str,
        name: str,
        description: str,
        scopes: list[str]
    ) -> dict:
        """
        Create or update an inbound app.
        
        Args:
            app_id: Unique app identifier
            name: Display name
            description: App description
            scopes: List of allowed scopes
        """
        print(f"\n📱 Creating Inbound App: {name}")
        
        payload = {
            "id": app_id,
            "name": name,
            "description": description,
            "enabled": True,
            "scopes": [{"name": scope, "description": f"Access to {scope}"} for scope in scopes]
        }
        
        with httpx.Client() as client:
            # Try to create, if exists, update
            response = client.post(
                f"{self.base_url}/app/inbound",
                headers=self._headers(),
                json=payload
            )
            
            if response.status_code == 200:
                print(f"  ✅ Created successfully")
                return response.json()
            elif response.status_code == 409:
                # Already exists, update it
                response = client.put(
                    f"{self.base_url}/app/inbound/{app_id}",
                    headers=self._headers(),
                    json=payload
                )
                if response.status_code == 200:
                    print(f"  ✅ Updated existing app")
                    return response.json()
            
            print(f"  ❌ Error: {response.status_code} - {response.text}")
            return {}
    
    def setup_agents(self):
        """Set up both agents."""
        print("\n🚀 Setting up Descope for IntelliFlow")
        print("=" * 50)
        
        # Agent A - Email Summarizer
        self.create_inbound_app(
            app_id="agent-a-summarizer",
            name="Agent A - Email Summarizer",
            description="AI agent for email fetching and summarization",
            scopes=[
                "email.read",
                "email.summarize",
                "calendar.delegate"
            ]
        )
        
        # Agent B - Calendar Manager
        self.create_inbound_app(
            app_id="agent-b-calendar",
            name="Agent B - Calendar Manager",
            description="AI agent for calendar event management",
            scopes=[
                "calendar.read",
                "calendar.write"
            ]
        )
        
        print("\n" + "=" * 50)
        print("✅ Descope setup complete!")
        print("\nNext steps:")
        print("1. Log in to Descope Console and verify the apps")
        print("2. Configure OAuth flows for user consent")
        print("3. Update .env with your project credentials")


def main():
    """Main entry point."""
    project_id = os.getenv("DESCOPE_PROJECT_ID")
    management_key = os.getenv("DESCOPE_MANAGEMENT_KEY")
    
    if not project_id or not management_key:
        print("❌ Error: DESCOPE_PROJECT_ID and DESCOPE_MANAGEMENT_KEY must be set")
        print("\nUsage:")
        print("  export DESCOPE_PROJECT_ID=your_project_id")
        print("  export DESCOPE_MANAGEMENT_KEY=your_key")
        print("  python setup-descope.py")
        sys.exit(1)
    
    setup = DescopeSetup(project_id, management_key)
    setup.setup_agents()


if __name__ == "__main__":
    main()
