import hashlib
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("SecureVault_Data/logs/audit_log.txt")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def calculate_hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def get_last_hash() -> str:
    if not LOG_FILE.exists():
        return "0" * 64
    try:
        with LOG_FILE.open("r", encoding="utf-8") as f:
            last = f.readlines()[-1].strip()
            if "curr_hash=" in last:
                return last.split("curr_hash=")[-1]
    except Exception:
        pass
    return "0" * 64

def write_audit_log(user: str, action: str, target: str, result: bool):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prev = get_last_hash()
    raw = f"{ts}|user={user}|action={action}|target={target}|result={'success' if result else 'fail'}|prev_hash={prev}"
    curr = calculate_hash(raw)
    entry = f"[{ts}] user={user} action={action} target={target} result={'success' if result else 'fail'} prev_hash={prev} curr_hash={curr}\n"
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(entry)

def verify_log_integrity(verbose: bool = True) -> bool:
    if not LOG_FILE.exists():
        if verbose: print("[!] No audit log found.")
        return True
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    prev_hash = "0" * 64
    tampered = False
    if verbose: print("\n=== Audit Log Integrity Report ===\n")
    for i, line in enumerate(lines, start=1):
        try:
            prev = line.split("prev_hash=")[-1].split(" ")[0]
            curr = line.split("curr_hash=")[-1]
            # rebuild same raw string used earlier
            mid = line.split("] ")[-1].rsplit(" prev_hash=", 1)[0]
            raw = f"{line[1:20]}|{mid}|prev_hash={prev}"  # approximate rebuild for hash comparison
            # safer recompute by reconstructing fields:
            parts = line.split(" ")
            ts = line.split("]")[0].strip("[")
            # build canonical raw string
            # parse fields user=..., action=..., target=..., result=...
            fields = {}
            for p in parts:
                if "=" in p and p.count("=")==1:
                    k,v = p.split("=",1)
                    fields[k]=v
            canonical = f"{ts}|user={fields.get('user','')}|action={fields.get('action','')}|target={fields.get('target','')}|result={fields.get('result','')}|prev_hash={prev}"
            recomputed = calculate_hash(canonical)
            if prev != prev_hash or recomputed != curr:
                if verbose: print(f" Entry #{i} — Tampered or Broken")
                tampered = True
            else:
                if verbose: print(f" Entry #{i} — Verified")
            prev_hash = curr
        except Exception:
            if verbose: print(f" Entry #{i} — Corrupted format")
            tampered = True
    if verbose:
        print("\n" + ("All good — no tampering detected." if not tampered else "Tampering detected!"))
    return not tampered
