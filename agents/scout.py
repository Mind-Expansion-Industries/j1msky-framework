#!/usr/bin/env python3
"""
SCOUT Agent - News & Intelligence Gathering
Part of J1MSKY Agent Team
"""

import os
import sys
import time
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

class ScoutAgent:
    def __init__(self):
        self.name = "SCOUT"
        self.status_file = Path('/tmp/agents/scout_status.json')
        self.feed_file = Path('/tmp/agents/scout_feed.json')
        self.log_file = Path('/tmp/agents/scout.log')
        
        self.news_sources = {
            "Hacker News": "https://hnrss.org/newest?count=5",
            "TechCrunch": "https://techcrunch.com/feed/",
            "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index"
        }
        
        self.cache = []
        self.running = True
        self.fetch_interval = 300  # 5 minutes
        
        self.log("SCOUT agent initialized")
        
    def log(self, message):
        """Write to agent log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
            
    def update_status(self, status, message=""):
        """Update status file"""
        data = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "message": message,
            "sources": list(self.news_sources.keys()),
            "articles_cached": len(self.cache)
        }
        with open(self.status_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def fetch_feed(self, name, url):
        """Fetch a single RSS feed"""
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'J1MSKY-Scout/1.0'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                data = response.read()
                
            root = ET.fromstring(data)
            items = root.findall('.//item')
            
            articles = []
            for item in items[:3]:  # Top 3
                title_elem = item.find('title')
                if title_elem is not None:
                    title = title_elem.text[:100] if title_elem.text else "No title"
                    articles.append({
                        "source": name,
                        "title": title,
                        "time": datetime.now().strftime("%H:%M"),
                        "fresh": True
                    })
                    
            return articles
            
        except Exception as e:
            self.log(f"Error fetching {name}: {e}")
            return []
            
    def fetch_all(self):
        """Fetch all news sources"""
        self.log("Starting news fetch...")
        self.update_status("FETCHING", "Collecting news...")
        
        all_articles = []
        
        for name, url in self.news_sources.items():
            articles = self.fetch_feed(name, url)
            all_articles.extend(articles)
            self.log(f"Fetched {len(articles)} from {name}")
            time.sleep(1)  # Be nice to servers
            
        # Update cache
        self.cache = all_articles[-20:]  # Keep last 20
        
        # Write to feed file
        with open(self.feed_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "articles": self.cache
            }, f, indent=2)
            
        self.log(f"Completed fetch: {len(all_articles)} articles")
        self.update_status("IDLE", f"Cached {len(self.cache)} articles")
        
    def run(self):
        """Main agent loop"""
        self.log("SCOUT entering main loop")
        self.update_status("RUNNING", "Agent active")
        
        # Initial fetch
        self.fetch_all()
        
        last_fetch = time.time()
        
        while self.running:
            try:
                # Check if it's time to fetch
                if time.time() - last_fetch > self.fetch_interval:
                    self.fetch_all()
                    last_fetch = time.time()
                    
                # Update heartbeat
                self.update_status("IDLE", f"Next fetch in {int(self.fetch_interval - (time.time() - last_fetch))}s")
                
                time.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                self.log("Shutting down...")
                self.update_status("STOPPED", "Keyboard interrupt")
                break
            except Exception as e:
                self.log(f"Error in main loop: {e}")
                time.sleep(30)  # Wait longer on error
                
        self.log("SCOUT agent stopped")

if __name__ == '__main__':
    agent = ScoutAgent()
    agent.run()
