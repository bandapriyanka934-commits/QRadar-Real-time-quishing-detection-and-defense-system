"""
QRadar — Real-Time Public Web Launcher with Live Phone Access & QR Code
Launches FastAPI backend + Cloudflare Tunnel and prints an instant scan-to-open QR code.
"""

import os
import sys
import time
import re
import signal
import subprocess
import urllib.request
import urllib.error

# Force UTF-8 stdout for crisp terminal QR code rendering on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
CLOUDFLARED_EXE = os.path.join(ROOT_DIR, "cloudflared.exe")

backend_process = None
tunnel_process = None
started_backend_here = False


def is_backend_healthy(url="http://127.0.0.1:8000/health", timeout=2):
    """Check if the backend is actively responding."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "QRadar-Launcher/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def cleanup():
    """Cleanly terminate backend and tunnel processes on exit."""
    global backend_process, tunnel_process, started_backend_here
    print("\n\033[93m[!] Stopping QRadar tunnel and services...\033[0m")
    if tunnel_process:
        try:
            tunnel_process.terminate()
            tunnel_process.kill()
        except Exception:
            pass
    if backend_process and started_backend_here:
        try:
            backend_process.terminate()
            backend_process.kill()
        except Exception:
            pass
    print("\033[92m[✓] Shutdown complete.\033[0m")


def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)


def print_banner(public_url):
    """Displays a modern CLI banner with the public HTTPS URL and a scannable QR code."""
    try:
        import qrcode
        has_qrcode = True
    except ImportError:
        has_qrcode = False

    print("\n" + "=" * 68)
    print("\033[96m   🛡️  QRADAR — LIVE PUBLIC PHONE & WEB LINK IS ACTIVE!  🛡️\033[0m")
    print("=" * 68)
    print(f"\n\033[92m  👉 LIVE WEBSITE LINK (FOR PHONES & COMPUTERS):\033[0m")
    print(f"     \033[1m\033[94m{public_url}\033[0m\n")
    print("  \033[97m✓ Anyone anywhere in the world on iOS / Android / PC can open this link!\033[0m")
    print("  \033[97m✓ HTTPS is active — Phone camera QR scanner & real-time analytics enabled!\033[0m\n")

    if has_qrcode:
        print("\033[93m  📱 SCAN THIS QR CODE WITH YOUR PHONE CAMERA TO OPEN INSTANTLY:\033[0m\n")
        try:
            qr = qrcode.QRCode(border=1)
            qr.add_data(public_url)
            qr.print_ascii(invert=True)
        except Exception:
            pass
    
    print("\n" + "=" * 68)
    print("  \033[90m• Local Development URL:\033[0m http://127.0.0.1:8000")
    print("  \033[90m• API Docs (Swagger):\033[0m    http://127.0.0.1:8000/docs")
    print("  \033[91m• Press Ctrl + C to stop the public server.\033[0m")
    print("=" * 68 + "\n")


def start_services():
    global backend_process, tunnel_process, started_backend_here
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if not os.path.exists(CLOUDFLARED_EXE):
        print(f"\033[91m[ERROR] cloudflared.exe not found at {CLOUDFLARED_EXE}\033[0m")
        return

    # 1. Check if backend is already running
    if is_backend_healthy():
        print("\033[92m[✓] Active QRadar backend detected on http://127.0.0.1:8000\033[0m")
    else:
        print("\033[96m[*] Starting QRadar FastAPI Backend on http://127.0.0.1:8000...\033[0m")
        backend_env = os.environ.copy()
        backend_env["PYTHONPATH"] = f"{ROOT_DIR};{BACKEND_DIR}"

        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=BACKEND_DIR,
            env=backend_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        started_backend_here = True

        # Wait up to 10s for startup
        started = False
        for _ in range(20):
            time.sleep(0.5)
            if is_backend_healthy():
                started = True
                break
        
        if not started:
            print("\033[93m[!] Backend taking longer to initialize, continuing with tunnel startup...\033[0m")

    # 2. Start Cloudflare Tunnel
    print("\033[96m[*] Initializing Secure Cloudflare Tunnel for mobile & global internet access...\033[0m")
    tunnel_process = subprocess.Popen(
        [CLOUDFLARED_EXE, "tunnel", "--url", "http://127.0.0.1:8000"],
        cwd=ROOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
    )

    public_url = None
    tunnel_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    # Read output until the public URL is discovered
    for line in iter(tunnel_process.stdout.readline, ""):
        match = tunnel_pattern.search(line)
        if match:
            public_url = match.group(0)
            break

    if not public_url:
        print("\033[91m[ERROR] Could not extract Cloudflare public tunnel URL.\033[0m")
        cleanup()
        return

    print_banner(public_url)

    # Keep alive
    try:
        while True:
            time.sleep(1)
            if tunnel_process.poll() is not None:
                print("\033[91m[!] Cloudflare tunnel closed.\033[0m")
                break
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    start_services()
