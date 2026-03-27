"""
Grant Assistant - Main Application
AI-powered grant discovery, matching, and application system
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

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Grant Assistant API")

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================
# DATA MODELS
# ============================================

class HealthCheck(BaseModel):
    status: str
    database: str

class TestUser(BaseModel):
    email: str
    password: str

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


# ============================================
# ROOT & HEALTH ENDPOINTS
# ============================================

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Grant Assistant API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    try:
        supabase.table("profiles").select("*").limit(1).execute()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status
    }


# ============================================
# USER AUTHENTICATION
# ============================================

@app.post("/test-create-user")
def test_create_user(user: TestUser):
    try:
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        
        return {
            "success": True,
            "user": response.user.email if response.user else None,
            "message": "User created successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# USER PROFILE ENDPOINTS
# ============================================

@app.post("/profile/{user_id}")
def update_profile(user_id: str, profile: UserProfile):
    try:
        profile_data = profile.dict(exclude_none=True)
        response = supabase.table("profiles").update(profile_data).eq("id", user_id).execute()
        
        if response.data:
            return {
                "success": True,
                "message": "Profile updated successfully",
                "profile": response.data[0]
            }
        else:
            return {
                "success": False,
                "error": "User not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/profile/{user_id}")
def get_profile(user_id: str):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        
        if response.data:
            return {
                "success": True,
                "profile": response.data[0]
            }
        else:
            return {
                "success": False,
                "error": "User not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# SCRAPER AGENT ENDPOINTS
# ============================================

@app.post("/scraper/run")
def run_scraper():
    try:
        agent = ScraperAgent()
        saved_count = agent.run()
        
        return {
            "success": True,
            "message": "Scraper completed",
            "grants_saved": saved_count
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# GRANT ENDPOINTS
# ============================================

@app.get("/grants")
def get_all_grants():
    try:
        response = supabase.table("opportunities").select("*").order("created_at", desc=True).execute()
        
        return {
            "success": True,
            "count": len(response.data),
            "grants": response.data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/grants/{grant_id}")
def get_grant(grant_id: str):
    try:
        response = supabase.table("opportunities").select("*").eq("id", grant_id).execute()
        
        if response.data:
            return {
                "success": True,
                "grant": response.data[0]
            }
        else:
            return {
                "success": False,
                "error": "Grant not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# ELIGIBILITY AGENT ENDPOINTS
# ============================================

@app.post("/eligibility/{user_id}")
def check_eligibility(user_id: str):
    try:
        agent = EligibilityAgent()
        result = agent.run_for_user(user_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/matches/{user_id}")
def get_user_matches(user_id: str):
    try:
        response = supabase.table("matches").select("*, opportunities(*)").eq("user_id", user_id).order("score", desc=True).execute()
        
        return {
            "success": True,
            "count": len(response.data),
            "matches": response.data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# DOCUMENT AGENT ENDPOINTS
# ============================================

@app.post("/application/create/{user_id}/{grant_id}")
def create_application(user_id: str, grant_id: str):
    """Create an application draft for a grant"""
    try:
        agent = DocumentAgent()
        result = agent.create_application_for_grant(user_id, grant_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/applications/{user_id}")
def get_user_applications(user_id: str):
    """Get all applications for a user"""
    try:
        agent = DocumentAgent()
        applications = agent.get_user_applications(user_id)
        
        return {
            "success": True,
            "count": len(applications),
            "applications": applications
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.put("/application/{application_id}/status")
def update_application_status(application_id: str, update: ApplicationUpdate):
    """Update application status (draft, submitted, approved, rejected)"""
    try:
        agent = DocumentAgent()
        result = agent.update_application_status(application_id, update.status)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# EMAIL AGENT ENDPOINTS
# ============================================

@app.post("/notify/{user_id}")
def send_notification(user_id: str):
    """Send email notification to a user about new matches"""
    try:
        agent = EmailAgent()
        result = agent.send_notification(user_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/notify/all")
def notify_all_users():
    """Send notifications to all users"""
    try:
        agent = EmailAgent()
        result = agent.notify_all_users()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# DASHBOARD ENDPOINT
# ============================================

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    """Serve the dashboard HTML page"""
    import os
    try:
        # Check if dashboard.html exists
        if os.path.exists("dashboard.html"):
            with open("dashboard.html", "r", encoding="utf-8") as f:
                html_content = f.read()
            # Replace localhost with production URL
            html_content = html_content.replace("http://localhost:8000", "")
            return HTMLResponse(content=html_content)
        else:
            return HTMLResponse(content="<h1>Dashboard file not found</h1><p>Please ensure dashboard.html exists</p>")
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading dashboard</h1><p>{str(e)}</p>")