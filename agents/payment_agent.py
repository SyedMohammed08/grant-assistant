"""
Payment Agent - Handles subscriptions and payments
"""

import os
from dotenv import load_dotenv

load_dotenv()


class PaymentAgent:
    
    def __init__(self):
        self.name = "Payment Agent"
        self.plans = {
            "free": {
                "name": "Free",
                "price": 0,
                "features": ["View grants"]
            },
            "basic": {
                "name": "Basic",
                "price": 29,
                "features": ["View grants", "Eligibility matching"]
            },
            "pro": {
                "name": "Pro",
                "price": 79,
                "features": ["View grants", "Eligibility matching", "Auto-filled applications"]
            },
            "business": {
                "name": "Business",
                "price": 199,
                "features": ["Everything", "Email notifications", "Priority support"]
            }
        }
    
    def create_checkout_session(self, user_id, plan):
        """
        Create checkout session (demo mode - no actual payment)
        """
        if plan not in self.plans:
            return {"success": False, "error": "Invalid plan"}
        
        plan_data = self.plans[plan]
        
        # For demo purposes, just return success
        # In production, this would create a Stripe checkout session
        return {
            "success": True,
            "checkout_url": f"/dashboard?plan={plan}&demo=true",
            "message": f"Demo mode: You selected the {plan_data['name']} plan (${plan_data['price']}/month)",
            "session_id": "demo_session_123"
        }
    
    def get_plans(self):
        """Return available subscription plans"""
        return self.plans