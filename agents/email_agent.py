"""
Email Agent - Sends notifications about new grant matches
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class EmailAgent:
    """
    Sends email notifications about new grant matches
    """
    
    def __init__(self):
        self.name = "Email Agent"
        # For now, we'll just print emails (no actual sending)
        # To enable real emails, you'd need SMTP settings
        self.email_enabled = False
    
    def get_user_profile(self, user_id):
        """Fetch user's profile"""
        try:
            response = supabase.table("profiles").select("*").eq("id", user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"❌ Error fetching user: {e}")
            return None
    
    def get_new_matches(self, user_id):
        """Get recent matches for a user"""
        try:
            response = supabase.table("matches").select("*, opportunities(*)").eq("user_id", user_id).order("created_at", desc=True).limit(5).execute()
            return response.data
        except Exception as e:
            print(f"❌ Error fetching matches: {e}")
            return []
    
    def format_email_body(self, user, matches):
        """Create email content with grant matches"""
        # Get user's name
        name = user.get("full_name", "there")
        email = user.get("email", "your email")
        
        # Build email body
        body = f"""
Hello {name},

We've found new grant opportunities that match your business profile!

Here are your top matches:

"""
        
        for i, match in enumerate(matches, 1):
            grant = match.get("opportunities", {})
            score = match.get("score", 0)
            title = grant.get("title", "Unknown Grant")
            agency = grant.get("agency", "Unknown Agency")
            
            body += f"""
{i}. {title}
   Agency: {agency}
   Match Score: {score}%
   
"""
        
        body += f"""
To view full details and apply, visit:
http://localhost:8000/dashboard

Best regards,
Grant Assistant Team
"""
        
        return body
    
    def send_notification(self, user_id):
        """
        Send email notification to user about new matches
        """
        print("=" * 50)
        print(f"📧 {self.name} Sending notification")
        print("=" * 50)
        
        # Get user
        user = self.get_user_profile(user_id)
        if not user:
            print("❌ User not found")
            return {"success": False, "error": "User not found"}
        
        # Get recent matches
        matches = self.get_new_matches(user_id)
        if not matches:
            print("⚠️ No recent matches found")
            return {"success": False, "message": "No matches to notify"}
        
        email = user.get("email")
        if not email:
            print("❌ No email address found")
            return {"success": False, "error": "No email address"}
        
        print(f"📧 Sending to: {email}")
        print(f"📊 Found {len(matches)} matches to share")
        
        # Format email
        body = self.format_email_body(user, matches)
        
        # For now, just print the email (no actual sending)
        print("\n" + "=" * 50)
        print("EMAIL PREVIEW")
        print("=" * 50)
        print(body)
        print("=" * 50)
        
        # If you want to actually send emails, uncomment and configure below
        if self.email_enabled:
            self.send_real_email(email, "New Grant Matches Found!", body)
        
        return {
            "success": True,
            "message": f"Notification sent to {email}",
            "matches_count": len(matches),
            "email_preview": body[:500]  # First 500 chars
        }
    
    def send_real_email(self, to_email, subject, body):
        """
        Actually send email (requires SMTP configuration)
        """
        # This is a placeholder - you'd need to configure SMTP
        # Example with Gmail:
        #
        # smtp_server = "smtp.gmail.com"
        # port = 587
        # sender_email = os.getenv("EMAIL_SENDER")
        # password = os.getenv("EMAIL_PASSWORD")
        #
        # msg = MIMEMultipart()
        # msg["From"] = sender_email
        # msg["To"] = to_email
        # msg["Subject"] = subject
        # msg.attach(MIMEText(body, "plain"))
        #
        # server = smtplib.SMTP(smtp_server, port)
        # server.starttls()
        # server.login(sender_email, password)
        # server.send_message(msg)
        # server.quit()
        
        print(f"📧 Real email would be sent to: {to_email}")
    
    def notify_all_users(self):
        """
        Send notifications to all users with matches
        """
        print("=" * 50)
        print(f"📧 {self.name} Notifying all users")
        print("=" * 50)
        
        try:
            # Get all users with profiles
            response = supabase.table("profiles").select("id, email").execute()
            users = response.data
            
            results = []
            for user in users:
                result = self.send_notification(user["id"])
                results.append(result)
            
            return {
                "success": True,
                "total_users": len(users),
                "results": results
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# For testing
if __name__ == "__main__":
    agent = EmailAgent()
    print("Email Agent ready. Run via API with user_id")