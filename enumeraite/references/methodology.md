# Enumeraite reasoning methodology

Read only the section matching the requested mode.

## Bulk API-path discovery

Input paths must start with `/`, be at most 200 characters, and contain neither `..` nor `//`.

Infer these dimensions before generating:

- API prefix and namespace: `/api`, `/rest`, `/internal`, `/admin`.
- Version style and placement: `v1`, `v2`, date versions, or no version.
- Resource vocabulary, plurality, abbreviations, and casing.
- Actions: CRUD verbs, authentication lifecycle, imports/exports, batch operations.
- Nesting and relationships: parent/resource/identifier/child.
- Identifier style: integers, UUIDs, usernames, slugs; use only concrete values.
- Framework or organization conventions evidenced by the seeds.

Generate in this priority order:

1. Near-neighbor transformations supported by multiple seeds.
2. Missing CRUD or lifecycle siblings in the same style.
3. Lateral resource and version variants.
4. Role, admin, internal, health, debug, or legacy variants only when compatible with the observed grammar.
5. Deeper nested variants, capped at 10 slash separators.

Do not merely append a generic wordlist. Preserve prefix, delimiter, plurality, abbreviation, and action placement. Remove original seeds and normalized duplicates.

Optional ranking heuristic adapted from the project:

- Begin at 0.5.
- Compute Jaccard similarity between candidate and seed path segments.
- Raise to `0.3 + 0.5 × best_similarity` when higher.
- Add 0.1 for an evidenced common family such as `api`, `user`, `admin`, or `auth`.
- Cap at 1.0 and treat the number only as relative ranking.

## Bulk subdomain discovery

Input must be a full dotted hostname. Keep total length at most 250 characters and each label at most 63. Labels may contain letters, digits, hyphens, and observed underscores; reject empty labels, `..`, slashes, and leading/trailing hyphens.

Separate the stable domain suffix from the variable host pattern using the common suffix across seeds. Do not guess a registrable domain from a single unfamiliar public suffix; preserve all stable trailing labels instead.

Decompose host labels into likely components:

- service or role: `api`, `web`, `db`, `admin`, `auth`;
- environment: `dev`, `test`, `stage`, `prod`;
- region or zone: `us-east-1`, `use1`, `eu1`, `az2`;
- product or business unit;
- action or lifecycle verb;
- instance family and zero-padded ordinal: `web01`, `cx02`;
- separators, component order, and casing.

Generate controlled variants by changing one high-confidence component first, then combine two components only where seeds demonstrate that composition. Preserve the stable suffix. Prefer vocabulary learned from the seeds; use common infrastructure alternatives only to fill an obvious component class. Avoid broad unrelated subdomain spraying.

Rank by exact suffix preservation, component-position fidelity, separator fidelity, and the number of substitutions supported by seed evidence.

## Single-subdomain pattern analysis

Return this structure in Markdown or JSON as requested:

```json
{
  "original_subdomain": "input.example.com",
  "decomposition": [
    {
      "value": "component",
      "type": "service|product|environment|region|zone|instance|domain|other",
      "description": "evidence-based interpretation",
      "alternatives": ["alt1", "alt2"]
    }
  ],
  "reasoning": "how the separators, positions, and vocabulary imply the pattern",
  "pattern_template": "<service>-<environment>-<instance>.<stable-domain>",
  "generated_variants": ["variant.example.com"],
  "confidence_score": 0.0
}
```

Preserve ambiguity. If a token could be a region or product code, say so and lower confidence rather than inventing certainty. Validate every generated variant with the subdomain rules above.

## Function-specific path analysis

Input requires one valid path and a functionality phrase such as `user deletion` or `admin operations`.

Break the path into ordered components with these preferred types: `api_prefix`, `version`, `namespace`, `resource`, `action`, `parameter`, `identifier`. Infer the source convention before translating the requested function. Consider full words and evidenced abbreviations (`create/crt`, `delete/del/dlt/rmv`, `update/upd`), RESTful resource forms, action endpoints, batch forms, version siblings, and privileged namespaces.

Return this structure:

```json
{
  "original_path": "/api/v1/users",
  "function_context": "user deletion",
  "path_breakdown": [
    {
      "value": "api",
      "type": "api_prefix",
      "description": "API namespace",
      "position": 0
    }
  ],
  "function_analysis": "how this codebase's conventions would express the function",
  "reasoning": "why each generated form is plausible",
  "generated_paths": ["/api/v1/users/123/delete"],
  "confidence_score": 0.0
}
```

Generated paths must start with `/`, be at most 200 characters, contain neither `..` nor `//`, and have no more than 10 slash separators. Do not assume an HTTP method confirms endpoint existence; path-only generation cannot determine methods or authorization behavior.
