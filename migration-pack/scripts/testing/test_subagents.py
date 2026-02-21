#!/usr/bin/env python3
"""Test subagent spawning for Agent Teams v4.0"""

import requests
import time
import sys

BASE_URL = "http://localhost:8080"

def test_spawn():
    print("Testing Agent Teams v4.0 Subagent Spawning...")
    print("=" * 50)
    
    # Test 1: Check server is up
    try:
        r = requests.get(BASE_URL, timeout=5)
        if r.status_code == 200:
            print("✓ Server is running")
        else:
            print(f"✗ Server returned {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Server not accessible: {e}")
        return False
    
    # Test 2: Spawn Kimi subagent
    print("\nSpawning Kimi K2.5 subagent...")
    try:
        r = requests.post(f"{BASE_URL}/api/spawn", 
                         data={"model": "k2p5", "task": "Test task: Say hello"},
                         timeout=10)
        result = r.json()
        if result.get('success'):
            print(f"✓ Spawned: {result['agent_id'][:30]}...")
        else:
            print(f"✗ Spawn failed: {result.get('error')}")
    except Exception as e:
        print(f"✗ Spawn error: {e}")
    
    # Test 3: Spawn Sonnet subagent
    print("\nSpawning Claude Sonnet subagent...")
    try:
        r = requests.post(f"{BASE_URL}/api/spawn",
                         data={"model": "sonnet", "task": "Test task: Write a poem"},
                         timeout=10)
        result = r.json()
        if result.get('success'):
            print(f"✓ Spawned: {result['agent_id'][:30]}...")
        else:
            print(f"✗ Spawn failed: {result.get('error')}")
    except Exception as e:
        print(f"✗ Spawn error: {e}")
    
    # Test 4: Spawn team
    print("\nSpawning Code Team...")
    try:
        r = requests.post(f"{BASE_URL}/api/spawn-team",
                         data={"team": "team_coding", "task": "Test team deployment"},
                         timeout=10)
        result = r.json()
        if result.get('success'):
            print(f"✓ Team spawned: {result['team']}")
        else:
            print(f"✗ Team spawn failed: {result.get('error')}")
    except Exception as e:
        print(f"✗ Team spawn error: {e}")
    
    print("\n" + "=" * 50)
    print("Test complete! Check dashboard at http://localhost:8080")
    print("Go to 'Subagents' tab to see spawned agents")
    return True

if __name__ == '__main__':
    test_spawn()
