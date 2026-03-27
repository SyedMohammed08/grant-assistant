"""
Payment Agent - Handles subscriptions and payments via Stripe
"""

import os
import stripe
from dotenv import load_dotenv

load_dotenv()

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


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
        Create Stripe checkout session for subscription
        """
        if plan not in self.plans:
            return {"success": False, "error": "Invalid plan"}
        
        if not STRIPE_SECRET_KEY:
            return {"success": False, "error": "Stripe not configured. Add STRIPE_SECRET_KEY to .env"}
        
        plan_data = self.plans[plan]
        
        try:
            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Grant Assistant - {plan_data['name']} Plan",
                            "description": f"Monthly subscription with features: {', '.join(plan_data['features'])}",
                        },
                        "unit_amount": plan_data["price"] * 100,
                        "recurring": {
                            "interval": "month",
                        },
                    },
                    "quantity": 1,
                }],
                mode="subscription",
                success_url="https://grant-assistant.onrender.com/dashboard?success=true",
                cancel_url="https://grant-assistant.onrender.com/dashboard?canceled=true",
                metadata={
                    "user_id": user_id,
                    "plan": plan
                }
            )
            
            return {
                "success": True,
                "checkout_url": session.url,
                "session_id": session.id
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_plans(self):
        """
        Return available subscription plans
        """
        return self.plans