#!/usr/bin/env python3
"""
Test script to check Telegram API connectivity
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_telegram_api():
    """Test if we can reach Telegram API"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ No bot token found")
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    
    print(f"🔍 Testing connection to: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            print(f"✅ Response status: {response.status_code}")
            print(f"✅ Response: {response.text}")
            
    except httpx.ConnectTimeout:
        print("❌ Connection timeout - cannot reach Telegram API")
    except httpx.ConnectError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Other error: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram_api())
