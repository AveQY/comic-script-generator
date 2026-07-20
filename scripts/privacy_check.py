#!/usr/bin/env python3
"""Privacy/safety scanner for comic-script-generator skill releases.

Checks git-tracked and working-tree text files for credential-like values,
private deployment details, and accidental real config files. This script is
intentionally conservative: allowlist placeholders and documentation examples;
flag real-looking values before publishing or syncing the skill.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {'.git', '__pycache__', '.pytest_cache', 'venv', 'env', '.venv'}
TEXT_SUFFIXES = {'.md', '.py', '.json', '.yaml', '.yml', '.txt', '.toml', '.ini', '.sh', '.html'}
ALLOWLIST_SUBSTRINGS = {
    '<your-image-api-domain>', '<your-private-token>', '<host>', '<KEY>', '<SERVER_IP>',
    '<your-server-ip>', '<path>', '<项目名>', 'Bearer ***', 'Bearer <private-token>',
    'Bearer <your-private-token>', 'https://<host>', 'https://<your-image-api-domain>',
    'YOUR_DOMAIN', 'config.example.json', 'api.example.com', 'example.com',
    '127.0.0.1', 'localhost', '0.0.0.0', 'VPN/代理', 'VPN/proxy', 'proxy details',
    'proxy may be restarting', 'Mihomo/Clash-style proxy', 'local-only proxy',
    'proxy subscriptions', 'keep subscription URLs', 'api[_-]?key',
    'API_KEY', '_get_api_key', 'encodeURIComponent(apiKey)',
}

PATTERNS = [
    ('real_bearer_token', re.compile(r'Bearer\s+(?!<|\*{3})[A-Za-z0-9._\-]{12,}')),
    ('openai_like_key', re.compile(r'\bsk-[A-Za-z0-9_\-]{20,}\b')),
    ('generic_secret_assignment', re.compile(r'(?i)\b(api[_-]?key|secret|token|password|authorization)\b\s*[:=]\s*["\']?(?!<|\*{3}|$)[^"\'\s]{12,}')),
    ('public_ipv4', re.compile(r'(?<![\d.])(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-5])(?:\.(?:\d{1,3})){3}(?![\d.])')),
    ('private_domain_aweqy', re.compile(r'(?i)\b[a-z0-9.-]*aweqy\.top\b')),
    ('absolute_private_path', re.compile(r'/(home/ubuntu|root/comic-projects|root/\.config|root/\.hermes)(?:/|\b)')),
    ('vpn_or_proxy_subscription', re.compile(r'(?i)(ss://|vmess://|vless://|trojan://)')),
]


def iter_files(root: Path):
    for p in root.rglob('*'):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if not p.is_file():
            continue
        if p.name == 'privacy_check.py':
            continue
        if p.name == 'config.json':
            yield p
            continue
        if p.suffix.lower() in TEXT_SUFFIXES:
            yield p


def is_binary(p: Path) -> bool:
    try:
        chunk = p.read_bytes()[:2048]
    except Exception:
        return True
    return b'\0' in chunk


def allowed(line: str) -> bool:
    return any(s in line for s in ALLOWLIST_SUBSTRINGS)


def scan(root: Path):
    findings = []
    for p in iter_files(root):
        rel = str(p.relative_to(root))
        if p.name == 'config.json':
            findings.append((rel, 0, 'real_config_file', 'Real config.json must not live inside the skill; use ~/.config/comic-script-generator/image_config.json'))
            continue
        if is_binary(p):
            continue
        text = p.read_text(encoding='utf-8', errors='ignore')
        for i, line in enumerate(text.splitlines(), 1):
            if allowed(line):
                continue
            for name, pat in PATTERNS:
                if pat.search(line):
                    # Avoid flagging harmless references to env var names.
                    if name == 'generic_secret_assignment' and ('os.environ.get' in line or 'add_argument' in line):
                        continue
                    findings.append((rel, i, name, line.strip()[:240]))
    return findings


def main():
    ap = argparse.ArgumentParser(description='Scan skill files for accidental secrets/private deployment data')
    ap.add_argument('--root', default=str(Path(__file__).resolve().parents[1]), help='skill root directory')
    ap.add_argument('--json', action='store_true', help='emit JSON')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    findings = scan(root)
    result = {'root': str(root), 'ok': not findings, 'count': len(findings), 'findings': [
        {'file': f, 'line': line, 'type': typ, 'snippet': snip} for f, line, typ, snip in findings
    ]}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if findings:
            print(f'PRIVACY CHECK FAILED: {len(findings)} finding(s)')
            for f, line, typ, snip in findings[:200]:
                loc = f'{f}:{line}' if line else f
                print(f'- {loc} [{typ}] {snip}')
        else:
            print('PRIVACY CHECK PASSED: no credential/private deployment findings')
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
