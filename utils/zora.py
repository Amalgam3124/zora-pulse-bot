# utils/zora.py
import os
import subprocess
import json

BASE_DIR = os.path.dirname(__file__)
ZORA_SDK_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'zora-sdk'))
GET_PULSE_SCRIPT = os.path.join(ZORA_SDK_DIR, 'getPulseMetrics.js')
GET_COIN_SCRIPT  = os.path.join(ZORA_SDK_DIR, 'getCoinMetrics.js')

def _run_script(script_path: str, args: list[str]) -> str | None:
    try:
        proc = subprocess.run(
            ['node', script_path] + args,
            cwd=ZORA_SDK_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        print(f"❌ Failed to launch script {script_path}: {e}")
        return None

    stdout = proc.stdout.decode('utf-8', errors='ignore')
    stderr = proc.stderr.decode('utf-8', errors='ignore')

    if proc.returncode != 0:
        print(f"❌ Script {os.path.basename(script_path)} error:\n{stderr}")
        return None

    return stdout

def get_pulse_metrics() -> list[dict]:
    out = _run_script(GET_PULSE_SCRIPT, [])
    if not out:
        return []

    metrics = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            metrics.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"⚠️ Ignoring invalid JSON: {line}")
    return metrics

def get_coin_metrics(address: str) -> dict:
    out = _run_script(GET_COIN_SCRIPT, [address])
    if not out:
        return {}
    line = out.strip().splitlines()[0] if out.strip() else ''
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        print(f"⚠️ Could not parse JSON for {address}: {line}")
        return {}
