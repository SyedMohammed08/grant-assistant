"""
Grant Assistant - Main Application
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from agents.scraper_agent import ScraperAgent
from agents.eligibility_agent import EligibilityAgent
from agents.document_agent import DocumentAgent
from agents.email_agent import EmailAgent
from agents.payment_agent import PaymentAgent

load_dotenv()

app = FastAPI(title="Grant Assistant API")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class UserProfile(BaseModel):
    full_name: str = None
    business_name: str = None
    business_type: str = None
    industry: str = None
    state: str = None
    revenue_range: str = None
    years_in_business: int = None
    employees_count: int = None

class ApplicationUpdate(BaseModel):
    status: str


@app.get("/")
def read_root():
    return {"message": "Welcome to Grant Assistant API", "version": "0.1.0"}


@app.get("/health")
def health_check():
    try:
        supabase.table("profiles").select("*").limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "healthy", "database": f"error: {str(e)}"}


@app.get("/grants")
def get_all_grants():
    try:
        response = supabase.table("opportunities").select("*").order("created_at", desc=True).execute()
        return {"success": True, "count": len(response.data), "grants": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/scraper/run")
def run_scraper():
    try:
        agent = ScraperAgent()
        saved_count = agent.run()
        return {"success": True, "message": "Scraper completed", "grants_saved": saved_count}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/profile/{user_id}")
def update_profile(user_id: str, profile: UserProfile):
    try:
        profile_data = profile.dict(exclude_none=True)
        response = supabase.table("profiles").update(profile_data).eq("id", user_id).execute()
        if response.data:
            return {"success": True, "profile": response.data[0]}
        return {"success": False, "error": "User not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/profile/{user_id}")
def get_profile(user_id: str):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if response.data:
            return {"success": True, "profile": response.data[0]}
        return {"success": False, "error": "User not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/eligibility/{user_id}")
def check_eligibility(user_id: str):
    try:
        agent = EligibilityAgent()
        result = agent.run_for_user(user_id)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/matches/{user_id}")
def get_user_matches(user_id: str):
    try:
        response = supabase.table("matches").select("*, opportunities(*)").eq("user_id", user_id).order("score", desc=True).execute()
        return {"success": True, "count": len(response.data), "matches": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/application/create/{user_id}/{grant_id}")
def create_application(user_id: str, grant_id: str):
    try:
        agent = DocumentAgent()
        result = agent.create_application_for_grant(user_id, grant_id)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/applications/{user_id}")
def get_user_applications(user_id: str):
    try:
        agent = DocumentAgent()
        applications = agent.get_user_applications(user_id)
        return {"success": True, "count": len(applications), "applications": applications}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.put("/application/{application_id}/status")
def update_application_status(application_id: str, update: ApplicationUpdate):
    try:
        agent = DocumentAgent()
        result = agent.update_application_status(application_id, update.status)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/notify/{user_id}")
def send_notification(user_id: str):
    try:
        agent = EmailAgent()
        result = agent.send_notification(user_id)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# PAYMENT AGENT ENDPOINTS
# ============================================

@app.get("/plans")
def get_plans():
    """Get available subscription plans"""
    try:
        agent = PaymentAgent()
        return {"success": True, "plans": agent.get_plans()}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/checkout/{user_id}/{plan}")
def create_checkout(user_id: str, plan: str):
    """Create checkout session for subscription"""
    try:
        agent = PaymentAgent()
        result = agent.create_checkout_session(user_id, plan)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# DASHBOARD ENDPOINT
# ============================================

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    try:
        with open("dashboard.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>")