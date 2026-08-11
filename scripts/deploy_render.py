"""
Automated Deployment Script for Render via Render REST API.
"""

import os
import sys
import json
import httpx

RENDER_API_URL = "https://api.render.com/v1"


def deploy_to_render(api_key: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # 1. Get Owner Account ID
    print("[1] Fetching Render owner account details...")
    resp = httpx.get(f"{RENDER_API_URL}/owners", headers=headers)
    if resp.status_code != 200:
        print(f"[ERROR] Failed to authenticate API Key: {resp.status_code} {resp.text}")
        return

    owners = resp.json()
    if not owners:
        print("[ERROR] No owner account found.")
        return

    owner_id = owners[0]["owner"]["id"]
    owner_name = owners[0]["owner"]["name"]
    print(f"    Authenticated as owner: {owner_name} ({owner_id})")

    # 2. Create Web Service on Render
    print("\n[2] Creating Web Service 'fraud-detection-system' on Render...")
    payload = {
        "type": "web_service",
        "name": "fraud-detection-system",
        "ownerId": owner_id,
        "repo": "https://github.com/TanoojPuppala/fraud-detection-system",
        "autoDeploy": "yes",
        "branch": "main",
        "serviceDetails": {
          "env": "python",
          "envSpecificDetails": {
            "buildCommand": "pip install -r backend/requirements.txt && cd frontend && npm install && npm run build",
            "startCommand": "uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"
          },
          "region": "oregon",
          "plan": "free"
        }
    }

    create_resp = httpx.post(f"{RENDER_API_URL}/services", headers=headers, json=payload)
    if create_resp.status_code in [200, 201]:
        service_data = create_resp.json()
        svc = service_data.get("service", service_data)
        service_id = svc.get("id")
        url = svc.get("serviceDetails", {}).get("url") or f"https://{svc.get('slug')}.onrender.com"
        print(f"\n[+] SUCCESS! Web Service Created on Render:")
        print(f"    - Service ID: {service_id}")
        print(f"    - Live Production URL: {url}")
    else:
        print(f"[!] Creation response ({create_resp.status_code}): {create_resp.text}")


if __name__ == "__main__":
    api_key = os.getenv("RENDER_API_KEY")
    if not api_key and len(sys.argv) > 1:
        api_key = sys.argv[1]

    if not api_key:
        print("[ERROR] Please provide RENDER_API_KEY environment variable or argument.")
        sys.exit(1)

    deploy_to_render(api_key)
