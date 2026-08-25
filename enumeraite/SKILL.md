---
name: enumeraite
description: "Perform Enumeraite-style AI attack-surface enumeration directly in Codex: infer API-path or subdomain grammars from seeds, generate ranked candidates, decompose one subdomain pattern, derive function-specific API endpoints, and optionally validate authorized subdomains via DNS or HTTP. Use when the user asks for intelligent path/subdomain enumeration or invokes $enumeraite; no Enumeraite installation or external AI provider is required."
---

# Enumeraite

Reproduce the useful behavior of the Enumeraite project directly with Codex reasoning. Do not require the original package, its CLI, API keys, or an external AI provider. Use the bundled script only for deterministic filtering and authorized validation.

## Route the request

- Several known paths: bulk path discovery.
- Several known subdomains: bulk subdomain discovery.
- One subdomain plus a request to explain its naming: structured subdomain-pattern analysis.
- One API path plus desired functionality: structured function-specific path analysis.
- Candidate subdomains plus explicit authorization to contact them: optional DNS or HTTP validation.

Read [references/methodology.md](references/methodology.md) for the selected generation or analysis mode. Read [references/validation.md](references/validation.md) only when filtering candidates or performing DNS/HTTP validation.

## Guardrails

Use this skill only for systems the user owns or is authorized to assess. Pure candidate generation is non-networked. DNS and HTTP validation contact target infrastructure; require the user to place the targets in scope before running either operation. The validation script also requires `--authorized`.

Do not escalate from generation to validation implicitly. Do not fuzz paths, brute-force services, authenticate, exploit, or scan ports as part of this skill.

## Generation workflow

1. Load seeds from the prompt or file. Ignore blank lines and `#` comments. Reject malformed items before inference.
2. Infer the smallest grammar that explains the seeds: fixed root/prefix, variable components, separators, casing, abbreviations, versions, resources, actions, environments, regions, and instance identifiers.
3. Generate candidates by controlled substitutions and recombinations from that grammar. Preserve the target's observed style before adding common web conventions.
4. Use concrete values rather than placeholders such as `{id}`. Prefer plausible examples like `123`, `admin`, or a realistic UUID only where the seed grammar contains identifiers.
5. Validate shape, remove seeds, and deduplicate case-insensitively. For paths, also treat a trailing slash as equivalent. Use `scripts/enumeraite_tools.py filter` for large lists or file output.
6. Rank candidates by pattern fidelity, evidence from multiple seeds, and minimal edit distance. Confidence is a heuristic ranking signal, never a claim that an asset exists.
7. Return the requested count when enough valid candidates exist. If the grammar is weak, return fewer high-quality candidates and state the limitation.

## Output

- For bulk generation, default to a clean newline-delimited list when the output feeds another tool. Add a compact rationale or confidence column only when the user asks for analysis.
- For single-item analysis, use the structured schemas in the methodology reference and include both decomposition and generated variants.
- Clearly label results as `generated`, `DNS-resolving`, or `HTTP-responsive`; never call unvalidated candidates discovered or live.
- Preserve user-requested output paths and formats. Do not overwrite the seed file.

The original project contains provider adapters, configuration, and terminal UI that are unnecessary in skill form. This conversion retains its four reasoning modes, validation rules, normalization, confidence idea, and concurrent DNS/HTTP checks while removing external-provider setup and stale CLI architecture.
