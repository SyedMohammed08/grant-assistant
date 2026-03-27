"""
Document Agent - Auto-fills grant applications using user profile data
"""

import os
import json
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class DocumentAgent:
    """
    AI Agent that auto-fills grant applications
    """
    
    def __init__(self):
        self.name = "Document Agent"
    
    def get_user_profile(self, user_id):
        """Fetch user's business profile from database"""
        try:
            response = supabase.table("profiles").select("*").eq("id", user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"❌ Error fetching user: {e}")
            return None
    
    def get_grant(self, grant_id):
        """Fetch grant details from database"""
        try:
            response = supabase.table("opportunities").select("*").eq("id", grant_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"❌ Error fetching grant: {e}")
            return None
    
    def generate_application_draft(self, user_profile, grant):
        """
        Generate a draft application using user profile data
        """
        print(f"📝 Generating application for: {grant['title']}")
        
        # Current date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get business info from profile
        business_name = user_profile.get("business_name", "Your Business Name")
        full_name = user_profile.get("full_name", "Your Name")
        business_type = user_profile.get("business_type", "Business")
        industry = user_profile.get("industry", "Your Industry")
        state = user_profile.get("state", "Your State")
        years = user_profile.get("years_in_business", 0)
        employees = user_profile.get("employees_count", 0)
        
        # Generate application draft
        application = {
            "grant_title": grant["title"],
            "grant_agency": grant["agency"],
            "generated_date": today,
            "applicant_info": {
                "business_name": business_name,
                "contact_name": full_name,
                "business_type": business_type,
                "industry": industry,
                "state": state,
                "years_in_business": years,
                "employee_count": employees
            },
            "application_answers": {
                "question_1": f"Our business, {business_name}, is seeking funding to support our growth in the {industry} industry.",
                "question_2": f"We have been in business for {years} years and have {employees} employees.",
                "question_3": f"This grant would help us expand our operations and create new opportunities in {state}.",
                "question_4": f"We are confident that with this funding, we can achieve our business goals within 12 months."
            },
            "status": "draft",
            "notes": "This is an auto-generated draft. Please review and customize before submitting."
        }
        
        print(f"✅ Generated draft application")
        return application
    
    def save_application(self, user_id, grant_id, application_data):
        """
        Save application draft to database
        """
        try:
            # Check if application already exists
            existing = supabase.table("applications").select("*").eq("user_id", user_id).eq("opportunity_id", grant_id).execute()
            
            if not existing.data:
                # Insert new application
                result = supabase.table("applications").insert({
                    "user_id": user_id,
                    "opportunity_id": grant_id,
                    "submission_data": application_data,
                    "status": "draft",
                    "created_at": datetime.now().isoformat()
                }).execute()
                print(f"💾 Saved application draft")
                return result.data[0] if result.data else None
            else:
                # Update existing application
                result = supabase.table("applications").update({
                    "submission_data": application_data,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", existing.data[0]["id"]).execute()
                print(f"💾 Updated existing application")
                return result.data[0] if result.data else None
                
        except Exception as e:
            print(f"❌ Error saving application: {e}")
            return None
    
    def create_application_for_grant(self, user_id, grant_id):
        """
        Complete workflow: generate and save application for a grant
        """
        print("=" * 50)
        print(f"🤖 {self.name} Starting")
        print("=" * 50)
        
        # Get user profile
        user = self.get_user_profile(user_id)
        if not user:
            print("❌ User not found")
            return {"success": False, "error": "User not found"}
        
        # Get grant details
        grant = self.get_grant(grant_id)
        if not grant:
            print("❌ Grant not found")
            return {"success": False, "error": "Grant not found"}
        
        print(f"📋 User: {user.get('email', 'Unknown')}")
        print(f"📋 Grant: {grant['title'][:50]}...")
        
        # Generate application
        application = self.generate_application_draft(user, grant)
        
        # Save to database
        saved = self.save_application(user_id, grant_id, application)
        
        if saved:
            print(f"\n✅ {self.name} Complete!")
            print(f"📊 Application saved as draft")
            print("=" * 50)
            
            return {
                "success": True,
                "message": "Application draft created",
                "application_id": saved.get("id"),
                "application": application
            }
        else:
            return {
                "success": False,
                "error": "Failed to save application"
            }
    
    def get_user_applications(self, user_id):
        """
        Get all applications for a user
        """
        try:
            response = supabase.table("applications").select("*, opportunities(*)").eq("user_id", user_id).order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"❌ Error fetching applications: {e}")
            return []
    
    def update_application_status(self, application_id, status):
        """
        Update application status (draft, submitted, approved, rejected)
        """
        valid_statuses = ["draft", "submitted", "approved", "rejected"]
        
        if status not in valid_statuses:
            return {"success": False, "error": f"Invalid status. Must be one of: {valid_statuses}"}
        
        try:
            result = supabase.table("applications").update({
                "status": status,
                "submitted_at": datetime.now().isoformat() if status == "submitted" else None,
                "updated_at": datetime.now().isoformat()
            }).eq("id", application_id).execute()
            
            if result.data:
                return {"success": True, "application": result.data[0]}
            else:
                return {"success": False, "error": "Application not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# For testing
if __name__ == "__main__":
    agent = DocumentAgent()
    print("Document Agent ready. Run via API with user_id and grant_id")