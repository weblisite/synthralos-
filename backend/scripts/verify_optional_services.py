#!/usr/bin/env python3
# ruff: noqa: T201
"""
Verify Optional Services Configuration

This script checks if EasyOCR, Tweepy, and ChromaDB are properly configured
and working in the backend environment.
"""

import os
import sys

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from app.ocr.service import OCRService
from app.osint.service import OSINTService
from app.rag.service import RAGService


def check_easyocr():
    """Check if EasyOCR is installed and working."""
    print("\n" + "=" * 60)
    print("EasyOCR Verification")
    print("=" * 60)

    try:
        ocr_service = OCRService()
        easyocr_engine = ocr_service._ocr_engines.get("easyocr", {})

        if easyocr_engine.get("is_available", False):
            print("✅ EasyOCR: INSTALLED AND WORKING")
            print("   Status: Available")
            print("   Client: Initialized")
            return True
        else:
            print("❌ EasyOCR: NOT AVAILABLE")
            print("   Reason: Engine not initialized")
            print("   Action: Check Docker build logs for installation errors")
            return False
    except Exception as e:
        print(f"❌ EasyOCR: ERROR - {e}")
        return False


def check_tweepy():
    """Check if Tweepy is configured and working."""
    print("\n" + "=" * 60)
    print("Tweepy (Twitter API) Verification")
    print("=" * 60)

    # Check environment variables
    bearer_token = settings.TWITTER_BEARER_TOKEN
    api_key = settings.TWITTER_API_KEY
    api_secret = settings.TWITTER_API_SECRET

    print(f"   TWITTER_BEARER_TOKEN: {'✅ Set' if bearer_token else '❌ Not set'}")
    print(f"   TWITTER_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
    print(f"   TWITTER_API_SECRET: {'✅ Set' if api_secret else '❌ Not set'}")

    try:
        osint_service = OSINTService()
        tweepy_engine = osint_service._engines.get("tweepy", {})

        if tweepy_engine.get("is_available", False):
            auth_type = tweepy_engine.get("auth_type", "unknown")
            print("\n✅ Tweepy: CONFIGURED AND WORKING")
            print("   Status: Available")
            print(f"   Auth Type: {auth_type}")
            return True
        else:
            print("\n❌ Tweepy: NOT CONFIGURED")
            print("   Reason: Missing API credentials")
            print("   Action: Set TWITTER_BEARER_TOKEN in Render environment variables")
            print("   Get credentials from: https://developer.twitter.com/")
            return False
    except Exception as e:
        print(f"\n❌ Tweepy: ERROR - {e}")
        return False


def check_chromadb():
    """Check if ChromaDB is configured and working."""
    print("\n" + "=" * 60)
    print("ChromaDB Verification")
    print("=" * 60)

    # Check environment variables
    server_host = settings.CHROMA_SERVER_HOST
    server_port = settings.CHROMA_SERVER_HTTP_PORT
    auth_token = settings.CHROMA_SERVER_AUTH_TOKEN

    print(f"   CHROMA_SERVER_HOST: {'✅ Set' if server_host else '❌ Not set'}")
    print(f"   CHROMA_SERVER_HTTP_PORT: {server_port}")
    print(
        f"   CHROMA_SERVER_AUTH_TOKEN: {'✅ Set' if auth_token else '❌ Not set (optional)'}"
    )

    try:
        rag_service = RAGService()
        chromadb_client = rag_service._vector_db_clients.get("chromadb", {})

        if chromadb_client.get("is_available", False):
            print("\n✅ ChromaDB: CONFIGURED AND WORKING")
            print("   Status: Available")
            print(f"   Host: {server_host}:{server_port}")
            print("   Connection: Tested successfully")
            return True
        else:
            print("\n❌ ChromaDB: NOT CONFIGURED")
            print("   Reason: CHROMA_SERVER_HOST not set or connection failed")
            print("   Action: Set CHROMA_SERVER_HOST in Render environment variables")
            print("   Options:")
            print("   1. ChromaDB Cloud: Sign up at https://www.trychroma.com/")
            print("   2. Self-hosted: Deploy ChromaDB server and set host")
            return False
    except Exception as e:
        print(f"\n❌ ChromaDB: ERROR - {e}")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("Optional Services Configuration Verification")
    print("=" * 60)

    results = {
        "EasyOCR": check_easyocr(),
        "Tweepy": check_tweepy(),
        "ChromaDB": check_chromadb(),
    }

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for service, is_working in results.items():
        status = "✅ WORKING" if is_working else "❌ NOT CONFIGURED"
        print(f"{service:20} {status}")

    all_working = all(results.values())
    print("\n" + "=" * 60)
    if all_working:
        print("✅ All optional services are configured and working!")
    else:
        print("⚠️  Some services are not configured (this is OK - they're optional)")
        print("   See docs/OPTIONAL_SERVICES_SETUP.md for setup instructions")
    print("=" * 60 + "\n")

    return 0 if all_working else 1


if __name__ == "__main__":
    sys.exit(main())
