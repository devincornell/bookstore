#!/usr/bin/env python3
"""
Basic test script to test book research endpoints
Run this script to test the research endpoints manually
"""

import requests
import json
import sys
from typing import Dict, Any

# Base URL for the API (adjust if your server runs on a different port)
BASE_URL = "http://localhost:8000"

def test_get_research():
    """Test the GET /research endpoint"""
    print("Testing GET /research endpoint...")
    
    url = f"{BASE_URL}/research/research"
    params = {
        "title": "The Great Gatsby",
        "other_info": "F. Scott Fitzgerald"
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ GET /research - SUCCESS")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print("❌ GET /research - FAILED")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ GET /research - CONNECTION ERROR: {e}")
    
    print("-" * 50)

def test_get_list_books():
    """Test the GET /list_books endpoint"""
    print("Testing GET /list_books endpoint...")
    
    url = f"{BASE_URL}/research/list_books"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ GET /list_books - SUCCESS")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print("❌ GET /list_books - FAILED")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ GET /list_books - CONNECTION ERROR: {e}")
    
    print("-" * 50)


def test_post_research_and_insert():
    """Test the POST /research_and_insert endpoint"""
    print("Testing POST /research_and_insert endpoint...")
    
    url = f"{BASE_URL}/research/research_and_insert"
    payload = {
        "title": "1984",
        "author": "George Orwell",
        "save_to_database": True
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ POST /research_and_insert - SUCCESS")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print("❌ POST /research_and_insert - FAILED")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ POST /research_and_insert - CONNECTION ERROR: {e}")
    
    print("-" * 50)

def test_health_check():
    """Test if the server is running"""
    print("Testing server health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print("❌ Server health check failed")
            return False
    except requests.exceptions.RequestException:
        print("❌ Server is not running or not accessible")
        return False

def main():
    print("Book Research Endpoints Test Script")
    print("=" * 50)
    
    # Check if server is running
    if not test_health_check():
        print("\n⚠️  Make sure your FastAPI server is running on http://localhost:8000")
        print("You can start it with: uvicorn app.main:app --reload")
        sys.exit(1)
    
    print()
    
    # Test both endpoints
    #test_get_research()
    test_get_list_books()
    test_post_research_and_insert()
    
    print("Test script completed!")

if __name__ == "__main__":
    main()