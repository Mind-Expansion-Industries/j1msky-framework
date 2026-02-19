#!/usr/bin/env python3
"""
ARCHIVIST Agent - Documentation & File Organization
Part of J1MSKY Agent Team
"""

import os
import sys
import time
import json
import hashlib
from datetime import datetime
from pathlib import Path

class ArchivistAgent:
    def __init__(self):
        self.name = "ARCHIVIST"
        self.workspace = Path('/home/m1ndb0t/Desktop/J1MSKY')
        self.status_file = Path('/tmp/agents/archivist_status.json')
        self.log_file = Path('/tmp/agents/archivist.log')
        self.snapshot_file = Path('/tmp/agents/workspace_snapshot.json')
        
        self.running = True
        self.scan_interval = 3600  # Scan every hour
        self.file_cache = {}
        
        self.log("ARCHIVIST agent initialized")
        
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
            "files_tracked": len(self.file_cache)
        }
        with open(self.status_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def get_file_hash(self, filepath):
        """Get MD5 hash of file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()[:8]
        except:
            return "error"
            
    def scan_workspace(self):
        """Scan workspace and build file index"""
        self.log("Scanning workspace...")
        self.update_status("SCANNING", "Indexing files...")
        
        current_files = {}
        changes = []
        
        for root, dirs, files in os.walk(self.workspace):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                filepath = Path(root) / file
                try:
                    stat = filepath.stat()
                    file_hash = self.get_file_hash(filepath)
                    
                    current_files[str(filepath)] = {
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "hash": file_hash,
                        "type": filepath.suffix or "none"
                    }
                    
                    # Check if file is new or changed
                    if str(filepath) not in self.file_cache:
                        changes.append(f"NEW: {filepath.name}")
                    elif self.file_cache[str(filepath)]['hash'] != file_hash:
                        changes.append(f"MODIFIED: {filepath.name}")
                        
                except Exception as e:
                    pass
                    
        # Check for deleted files
        for old_path in self.file_cache:
            if old_path not in current_files:
                changes.append(f"DELETED: {Path(old_path).name}")
                
        # Update cache
        self.file_cache = current_files
        
        # Save snapshot
        with open(self.snapshot_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "files": current_files
            }, f, indent=2)
            
        # Report changes
        if changes:
            self.log(f"Detected {len(changes)} changes")
            for change in changes[:10]:  # Log first 10
                self.log(change)
        else:
            self.log("No changes detected")
            
        self.update_status("IDLE", f"Tracking {len(current_files)} files")
        return changes
        
    def update_inventory(self):
        """Update the INVENTORY.md file with current stats"""
        try:
            stats = {
                "total_files": len(self.file_cache),
                "python_files": sum(1 for f in self.file_cache.values() if f['type'] == '.py'),
                "markdown_files": sum(1 for f in self.file_cache.values() if f['type'] == '.md'),
                "scripts": sum(1 for f in self.file_cache.values() if f['type'] == '.sh'),
            }
            
            self.log(f"Stats: {stats['total_files']} files, {stats['python_files']} Python, {stats['markdown_files']} Markdown")
            
        except Exception as e:
            self.log(f"Error updating inventory: {e}")
            
    def run(self):
        """Main agent loop"""
        self.log("ARCHIVIST entering main loop")
        self.update_status("RUNNING", "Agent active")
        
        # Initial scan
        self.scan_workspace()
        self.update_inventory()
        
        last_scan = time.time()
        
        while self.running:
            try:
                # Check if it's time to scan
                if time.time() - last_scan > self.scan_interval:
                    changes = self.scan_workspace()
                    if changes:
                        self.update_inventory()
                    last_scan = time.time()
                    
                self.update_status("IDLE", f"Next scan in {int(self.scan_interval - (time.time() - last_scan))}s")
                
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                self.log("Shutting down...")
                self.update_status("STOPPED", "Keyboard interrupt")
                break
            except Exception as e:
                self.log(f"Error in main loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
                
        self.log("ARCHIVIST agent stopped")

if __name__ == '__main__':
    agent = ArchivistAgent()
    agent.run()
