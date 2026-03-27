"""
Payment Agent - Handles subscriptions and payments
"""

import os
from dotenv import load_dotenv

load_dotenv()


class PaymentAgent:
    """
    Handles user subscriptions and payments
    """
    
    def __init__(self):
        self.name = "Payment Agent"
        
        # Pricing plans
        self.plans = {
            "free": {
                "name": "Free",
                "price": 0,
                "price_display": "Free",
                "features": ["✓ View all grants", "✓ Basic search"],
                "color": "gray"
            },
            "basic": {
                "name": "Basic",
                "price": 29,
                "price_display": "$29",
                "features": ["✓ View all grants", "✓ Eligibility matching", "✓ Match scores (0-100%)"],
                "color": "blue"
            },
            "pro": {
                "name": "Pro",
                "price": 79,
                "price_display": "$79",
                "features": ["✓ Everything in Basic", "✓ Auto-filled applications", "✓ Application drafts", "✓ Email support"],
                "color": "purple"
            },
            "business": {
                "name": "Business",
                "price": 199,
                "price_display": "$199",
                "features": ["✓ Everything in Pro", "✓ Priority support", "✓ Custom grant alerts", "✓ Team access"],
                "color": "gold"
            }
        }
    
    def create_checkout_session(self, user_id, plan):
        """
        Create checkout session for subscription
        For demo, returns a success message
        To enable real payments, add Stripe integration
        """
        if plan not in self.plans:
            return {"success": False, "error": "Invalid plan"}
        
        plan_data = self.plans[plan]
        
        # Demo mode - return success without actual payment
        return {
            "success": True,
            "checkout_url": f"https://grant-assistant.onrender.com/dashboard?plan={plan}&status=success",
            "message": f"Demo: You selected the {plan_data['name']} plan ({plan_data['price_display']}/month)",
            "session_id": f"demo_{user_id}_{plan}",
            "demo": True
        }
    
    def get_plans(self):
        """Return available subscription plans"""
        return self.plans
    
    def verify_subscription(self, user_id):
        """Check if user has an active subscription"""
        # Demo: Always return basic plan for testing
        return {
            "success": True,
            "has_subscription": True,
            "plan": "basic",
            "status": "active"
        }