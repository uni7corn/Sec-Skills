#!/usr/bin/env python3
"""Filter and validate Enumeraite-style path and subdomain candidates."""

from __future__ import annotations

import argparse
import json
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable


def read_items(path: str | None) -> list[str]:
    if path:
        text = Path(path).read_text(encoding="utf-8")
        lines = text.splitlines()
    else:
        lines = sys.stdin
    return [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]


def valid_path(value: str, max_depth: int = 10) -> bool:
    return (
        value.startswith("/")
        and len(value) <= 200
        and ".." not in value
        and "//" not in value
        and value.count("/") <= max_depth
        and not any(ch.isspace() for ch in value)
    )


def valid_subdomain(value: str) -> bool:
    if not value or len(value) > 250 or "." not in value:
        return False
    if "/" in value or ".." in value or any(ch.isspace() for ch in value):
        return False
    labels = value.rstrip(".").split(".")
    if len(labels) < 2:
        return False
    for label in labels:
        if not label or len(label) > 63 or label.startswith("-") or label.endswith("-"):
            return False
        if not re.fullmatch(r"[A-Za-z0-9_-]+", label):
            return False
    return True


def normalize(value: str, kind: str) -> str:
    return value.lower().rstrip("/" if kind == "path" else ".")


def filter_items(candidates: Iterable[str], seeds: Iterable[str], kind: str) -> list[str]:
    validator = valid_path if kind == "path" else valid_subdomain
    known = {normalize(item, kind) for item in seeds if validator(item)}
    seen: set[str] = set()
    result: list[str] = []
    for raw in candidates:
        item = raw.strip()
        if kind == "subdomain":
            item = item.lower().rstrip(".")
        key = normalize(item, kind)
        if validator(item) and key not in known and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def write_lines(lines: Iterable[str], output: str | None) -> None:
    text = "\n".join(lines)
    if text:
        text += "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def dns_one(name: str) -> dict:
    started = time.perf_counter()
    try:
        infos = socket.getaddrinfo(name, None, type=socket.SOCK_STREAM)
        addresses = list(dict.fromkeys(info[4][0] for info in infos))
        return {
            "subdomain": name,
            "resolves": bool(addresses),
            "ip_addresses": addresses,
            "response_time": round(time.perf_counter() - started, 6),
            "error": None,
        }
    except Exception as exc:
        return {
            "subdomain": name,
            "resolves": False,
            "ip_addresses": [],
            "response_time": round(time.perf_counter() - started, 6),
            "error": str(exc),
        }


def run_dns(names: list[str], workers: int, timeout: float) -> list[dict]:
    socket.setdefaulttimeout(timeout)
    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(dns_one, name): name for name in names}
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as exc:
                results[name] = {"subdomain": name, "resolves": False, "ip_addresses": [], "response_time": 0.0, "error": str(exc)}
    return [results[name] for name in names]


TITLE_RE = re.compile(br"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def http_one(name: str, protocol: str, timeout: float, insecure: bool) -> dict:
    url = f"{protocol}://{name}"
    started = time.perf_counter()
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Enumeraite-Skill/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )
    context = None
    if protocol == "https" and insecure:
        context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            body = response.read(1_000_000)
            status = response.getcode()
            headers = response.headers
        error = None
    except urllib.error.HTTPError as exc:
        body = exc.read(1_000_000)
        status = exc.code
        headers = exc.headers
        error = None
    except Exception as exc:
        return {
            "subdomain": name,
            "url": url,
            "responsive": False,
            "status_code": None,
            "protocol": protocol,
            "title": None,
            "server": None,
            "response_time": round(time.perf_counter() - started, 6),
            "error": str(exc),
        }
    title_match = TITLE_RE.search(body)
    title = None
    if title_match:
        title = re.sub(r"\s+", " ", title_match.group(1).decode("utf-8", errors="replace")).strip()[:100]
    return {
        "subdomain": name,
        "url": url,
        "responsive": True,
        "status_code": status,
        "protocol": protocol,
        "title": title,
        "server": headers.get("Server"),
        "response_time": round(time.perf_counter() - started, 6),
        "error": error,
    }


def run_http(names: list[str], workers: int, timeout: float, both: bool, insecure: bool) -> list[dict]:
    protocols = ("https", "http") if both else ("https",)
    gathered: dict[str, list[dict]] = {name: [] for name in names}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(http_one, name, protocol, timeout, insecure): (name, protocol)
            for name in names for protocol in protocols
        }
        for future in as_completed(futures):
            name, protocol = futures[future]
            try:
                gathered[name].append(future.result())
            except Exception as exc:
                gathered[name].append({"subdomain": name, "url": f"{protocol}://{name}", "responsive": False, "status_code": None, "protocol": protocol, "title": None, "server": None, "response_time": 0.0, "error": str(exc)})
    chosen: list[dict] = []
    for name in names:
        options = gathered[name]
        options.sort(key=lambda item: (not item["responsive"], item["protocol"] != "https"))
        chosen.append(options[0])
    return chosen


def require_authorized(args: argparse.Namespace) -> None:
    if not args.authorized:
        raise SystemExit("Refusing network validation without --authorized.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    filter_parser = sub.add_parser("filter", help="Validate, exclude seeds, and deduplicate candidates")
    filter_parser.add_argument("--kind", choices=("path", "subdomain"), required=True)
    filter_parser.add_argument("--seeds")
    filter_parser.add_argument("--candidates", help="Candidate file; omit to read stdin")
    filter_parser.add_argument("--output")

    dns_parser = sub.add_parser("dns", help="Resolve authorized subdomain candidates")
    dns_parser.add_argument("--input", required=True)
    dns_parser.add_argument("--output")
    dns_parser.add_argument("--workers", type=int, default=20)
    dns_parser.add_argument("--timeout", type=float, default=5.0)
    dns_parser.add_argument("--existing-only", action="store_true")
    dns_parser.add_argument("--authorized", action="store_true")

    http_parser = sub.add_parser("http", help="Request authorized subdomain candidates")
    http_parser.add_argument("--input", required=True)
    http_parser.add_argument("--output")
    http_parser.add_argument("--workers", type=int, default=10)
    http_parser.add_argument("--timeout", type=float, default=10.0)
    http_parser.add_argument("--both", action="store_true")
    http_parser.add_argument("--insecure", action="store_true")
    http_parser.add_argument("--accessible-only", action="store_true")
    http_parser.add_argument("--authorized", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "filter":
        seeds = read_items(args.seeds) if args.seeds else []
        candidates = read_items(args.candidates)
        write_lines(filter_items(candidates, seeds, args.kind), args.output)
        return 0

    require_authorized(args)
    names = filter_items(read_items(args.input), [], "subdomain")
    if args.command == "dns":
        results = run_dns(names, args.workers, args.timeout)
        lines = ([item["subdomain"] for item in results if item["resolves"]] if args.existing_only else [json.dumps(item, ensure_ascii=False) for item in results])
    else:
        results = run_http(names, args.workers, args.timeout, args.both, args.insecure)
        lines = ([item["subdomain"] for item in results if item["responsive"]] if args.accessible_only else [json.dumps(item, ensure_ascii=False) for item in results])
    write_lines(lines, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
