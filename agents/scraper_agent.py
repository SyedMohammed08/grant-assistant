"""
Scraper Agent - Finds and saves grants from websites
"""

import requests
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class ScraperAgent:
    def __init__(self):
        self.name = "Scraper Agent"
    
    def run(self):
        """Main method to run the scraper"""
        print("=" * 50)
        print(f"🤖 {self.name} Running...")
        print("=" * 50)
        
        # Grant data to save
        grants = [
            {
                "title": "Small Business Innovation Research (SBIR) Grant",
                "description": "Funding for small businesses to conduct R&D with commercialization potential.",
                "agency": "Small Business Administration",
                "amount_min": 50000,
                "amount_max": 250000,
                "deadline": "2024-12-31",
                "source_url": "https://www.sbir.gov/about"
            }
        ]
        
        saved_count = 0
        
        for grant in grants:
            try:
                # Check if grant already exists
                existing = supabase.table("opportunities").select("*").eq("title", grant["title"]).execute()
                
                if not existing.data:
                    # Save new grant
                    supabase.table("opportunities").insert(grant).execute()
                    saved_count += 1
                    print(f"💾 Saved: {grant['title']}")
                else:
                    print(f"⏭️ Already exists: {grant['title']}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n✅ Complete! Saved {saved_count} new grants")
        print("=" * 50)
        
        return saved_count


# For testing
if __name__ == "__main__":
    agent = ScraperAgent()
    agent.run()