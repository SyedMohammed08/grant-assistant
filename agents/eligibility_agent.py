"""
Eligibility Agent - Matches grants to users based on business profile
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class EligibilityAgent:
    """
    Matches grants to users based on eligibility criteria
    """
    
    def __init__(self):
        self.name = "Eligibility Agent"
    
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
    
    def get_all_grants(self):
        """Fetch all grants from database"""
        try:
            response = supabase.table("opportunities").select("*").execute()
            return response.data
        except Exception as e:
            print(f"❌ Error fetching grants: {e}")
            return []
    
    def calculate_match_score(self, user_profile, grant):
        """
        Calculate match score (0-100) based on user and grant
        """
        score = 0
        reasons = []
        
        # 1. Industry match (30 points max)
        if user_profile.get("industry") and grant.get("agency"):
            if user_profile["industry"].lower() in grant["agency"].lower():
                score += 30
                reasons.append("✓ Industry matches grant agency")
            else:
                score += 10
                reasons.append("→ Generic match (industry not specifically targeted)")
        else:
            score += 15
            reasons.append("→ Open opportunity (no industry restriction)")
        
        # 2. Amount match (20 points)
        if grant.get("amount_max"):
            if grant["amount_max"] <= 100000:
                score += 20
                reasons.append("✓ Grant size suitable for small business")
            elif grant["amount_max"] <= 500000:
                score += 15
                reasons.append("→ Medium-sized grant opportunity")
            else:
                score += 10
                reasons.append("→ Large grant opportunity")
        else:
            score += 10
            reasons.append("→ Amount not specified")
        
        # 3. Location match (20 points if applicable)
        if user_profile.get("state"):
            score += 15
            reasons.append("✓ Location-based eligibility possible")
        else:
            score += 5
            reasons.append("→ Location not specified")
        
        # 4. Business type (20 points)
        if user_profile.get("business_type"):
            if user_profile["business_type"].lower() in ["llc", "corporation", "small business"]:
                score += 20
                reasons.append("✓ Business type eligible for most grants")
            else:
                score += 10
                reasons.append("→ Business type may have restrictions")
        else:
            score += 5
            reasons.append("→ Business type not specified")
        
        # 5. Years in business (10 points)
        if user_profile.get("years_in_business"):
            if user_profile["years_in_business"] >= 2:
                score += 10
                reasons.append("✓ Established business (2+ years)")
            else:
                score += 5
                reasons.append("→ New business (less than 2 years)")
        else:
            score += 5
            reasons.append("→ Years in business not specified")
        
        # Cap at 100
        score = min(score, 100)
        
        return {
            "score": score,
            "reasons": reasons,
            "summary": f"{score}% match based on {len(reasons)} criteria"
        }
    
    def match_user_with_grants(self, user_id):
        """
        Match a user with all grants and return sorted results
        """
        print(f"🤖 {self.name} matching grants for user: {user_id}")
        
        # Get user profile
        user = self.get_user_profile(user_id)
        if not user:
            print("❌ User not found")
            return []
        
        print(f"📋 User: {user.get('email', 'Unknown')}")
        
        # Get all grants
        grants = self.get_all_grants()
        if not grants:
            print("⚠️ No grants found in database")
            return []
        
        print(f"📊 Found {len(grants)} grants to evaluate")
        
        # Calculate matches
        matches = []
        for grant in grants:
            match = self.calculate_match_score(user, grant)
            matches.append({
                "grant": grant,
                "match_score": match["score"],
                "match_reasons": match["reasons"],
                "match_summary": match["summary"]
            })
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        print(f"✅ Found {len(matches)} matches")
        
        return matches
    
    def save_matches_to_database(self, user_id, matches):
        """
        Save match results to the database
        """
        saved_count = 0
        
        for match in matches:
            try:
                # Check if match already exists
                existing = supabase.table("matches").select("*").eq("user_id", user_id).eq("opportunity_id", match["grant"]["id"]).execute()
                
                if not existing.data:
                    # Save new match
                    supabase.table("matches").insert({
                        "user_id": user_id,
                        "opportunity_id": match["grant"]["id"],
                        "score": match["match_score"],
                        "status": "pending"
                    }).execute()
                    saved_count += 1
                    
            except Exception as e:
                print(f"❌ Error saving match: {e}")
        
        print(f"💾 Saved {saved_count} new matches to database")
        return saved_count
    
    def run_for_user(self, user_id):
        """
        Complete eligibility check for a user
        """
        print("=" * 50)
        print(f"🤖 {self.name} Starting")
        print("=" * 50)
        
        # Get matches
        matches = self.match_user_with_grants(user_id)
        
        if not matches:
            print("⚠️ No matches found")
            return {"success": False, "message": "No matches found", "matches": []}
        
        # Save to database
        saved = self.save_matches_to_database(user_id, matches)
        
        print(f"\n✅ {self.name} Complete!")
        print(f"📊 Top match: {matches[0]['grant']['title'][:50]}... ({matches[0]['match_score']}%)")
        print("=" * 50)
        
        return {
            "success": True,
            "total_matches": len(matches),
            "saved": saved,
            "top_match": {
                "title": matches[0]["grant"]["title"],
                "score": matches[0]["match_score"],
                "summary": matches[0]["match_summary"]
            },
            "matches": matches[:5]
        }


# For testing
if __name__ == "__main__":
    agent = EligibilityAgent()
    print("Eligibility Agent ready. Run via API with a user ID.")