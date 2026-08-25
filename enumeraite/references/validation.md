# Candidate filtering and validation

The bundled `scripts/enumeraite_tools.py` is self-contained and uses only the Python standard library.

## Filter generated candidates

Candidates can come from a file or standard input. Seeds are optional but should be supplied so known items are excluded.

```powershell
python .codex\skills\enumeraite\scripts\enumeraite_tools.py filter `
  --kind path --seeds .\known-paths.txt --candidates .\raw.txt `
  --output .\clean.txt
```

For subdomains, use `--kind subdomain`. Filtering preserves first occurrence order, lowercases subdomains, removes comments/blank lines, validates shape, removes seeds, and deduplicates. Paths preserve original case but compare case-insensitively with trailing slashes removed.

## DNS validation

Run only after the user confirms authorization for the candidate target scope:

```powershell
python .codex\skills\enumeraite\scripts\enumeraite_tools.py dns `
  --input .\candidates.txt --output .\dns-results.jsonl `
  --workers 20 --timeout 5 --authorized
```

Add `--existing-only` for a plain list of resolving names. DNS resolution is evidence that a name currently resolves, not that the service belongs to the expected application.

## HTTP validation

Run only with explicit authorization:

```powershell
python .codex\skills\enumeraite\scripts\enumeraite_tools.py http `
  --input .\resolving.txt --output .\http-results.jsonl `
  --both --workers 10 --timeout 10 --authorized
```

The default verifies TLS certificates. Use `--insecure` only when the user requests assessment of hosts with invalid/self-signed certificates. `--both` checks HTTPS and HTTP and prefers a responsive HTTPS result. Add `--accessible-only` for a plain list of responsive names.

HTTP-responsive means a request produced an HTTP status, including 4xx/5xx; it does not mean the application is healthy, vulnerable, or in scope beyond the authorization already given.
