"""
Scheduler - Runs scraper automatically
"""

import time
import schedule
from agents.scraper_agent import ScraperAgent
from datetime import datetime

def run_scraper_job():
    print(f"\n{'='*50}")
    print(f"⏰ Scheduled run at: {datetime.now()}")
    print(f"{'='*50}")
    agent = ScraperAgent()
    agent.run()

if __name__ == "__main__":
    print("🚀 Scheduler Started")
    print("=" * 50)
    
    # Run every 5 minutes for testing
    schedule.every(5).minutes.do(run_scraper_job)
    
    print("📅 Scraper runs every 5 minutes")
    print("Press Ctrl+C to stop\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)