#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import requests


def parse_args():
    parser = argparse.ArgumentParser(
        description="Monitor web pages for content changes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "url_file",
        type=argparse.FileType("r"),
        help="Text file with one URL per line (ignore blanks and # comments)",
    )
    parser.add_argument(
        "--state",
        type=Path,
        default=Path("webwatch_state.json"),
        help="State file for storing page hashes (default: webwatch_state.json)",
    )
    parser.add_argument(
        "--snapshots",
        type=Path,
        default=None,
        help="Directory to save snapshots of changed pages",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds (default: 10.0)",
    )
    return parser.parse_args()


def load_state(state_file):
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_state(state_file, state):
    fd, tmp_path = tempfile.mkstemp(dir=state_file.parent, prefix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp_path, state_file)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def compute_hash(content):
    return hashlib.sha256(content).hexdigest()


def fetch_url(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content, None
    except requests.RequestException as e:
        return None, str(e)


def save_snapshot(snapshots_dir, url, content):
    if not snapshots_dir:
        return
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    safe_name = url.replace("://", "_").replace("/", "_").replace(":", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}.html"
    filepath = snapshots_dir / filename
    with open(filepath, "wb") as f:
        f.write(content)


def log_change(url, status):
    timestamp = datetime.now().isoformat()
    with open("webwatch.log", "a") as f:
        f.write(f"{timestamp} {url} {status}\n")


def main():
    args = parse_args()

    urls = []
    for line in args.url_file:
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)

    state = load_state(args.state)

    for url in urls:
        content, error = fetch_url(url, args.timeout)

        if error:
            print(f"ERROR {url}", file=sys.stderr)
            log_change(url, "ERROR")
            continue

        current_hash = compute_hash(content)
        previous_hash = state.get(url)

        if previous_hash is None:
            status = "NEW"
            state[url] = current_hash
        elif current_hash != previous_hash:
            status = "CHANGED"
            state[url] = current_hash
            save_snapshot(args.snapshots, url, content)
        else:
            status = "UNCHANGED"

        print(f"{status} {url}")
        if status in ("NEW", "CHANGED"):
            log_change(url, status)

    save_state(args.state, state)


if __name__ == "__main__":
    main()
