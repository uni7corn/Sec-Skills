---
name: analyze-encrypted-web-traffic
description: Analyze authorized Web applications that encrypt HTTP request or response payloads at the application layer, reconstruct their cryptographic and serialization pipeline, and design or implement a transparent plaintext inspection proxy for debugging or security testing. Use with captured traffic, JavaScript bundles, mobile/Web client code, or proxy requirements involving SM2, RSA, AES, hybrid encryption, signatures, custom encodings, mitmproxy, Burp Suite, or similar tooling.
---

# Analyze Encrypted Web Traffic

Work only on systems the user is authorized to test. Treat keys, tokens, decrypted payloads, and captures as sensitive; do not echo complete secrets unless the user explicitly needs them in a controlled artifact.

## Workflow

### 1. Establish the evidence set

Collect representative encrypted requests and responses, relevant client bundles or source maps, request metadata, and the intended proxy topology. Record host/path scope and distinguish application-layer encryption from TLS.

If evidence is incomplete, continue with labeled hypotheses and list the smallest artifact needed to verify each one. Never present an inferred key, mode, or framing rule as confirmed.

### 2. Reconstruct the transform pipeline

Trace from the network boundary inward and identify, in order:

1. Plaintext serialization and canonicalization.
2. Optional compression, padding, nonce/IV generation, timestamps, or associated data.
3. Encryption, key wrapping/agreement, MAC, and signature operations.
4. Ciphertext framing and field layout.
5. Outer encoding such as hex, Base64, Base64URL, JSON, or binary.

Search call sites as well as primitive names. Follow `fetch`, XHR, Axios interceptors, WebSocket handlers, native bridges, request wrappers, response interceptors, and obfuscated dispatch tables. Record file and line locations when available.

Read [references/adapters.md](references/adapters.md) when selecting algorithm-specific checks or mapping the recovered pipeline onto a proxy adapter.

### 3. Produce an evidence matrix

For every request and response direction, report:

| Property | Observed value | Evidence | Confidence |
|---|---|---|---|
| Triggering endpoints/content types | | | |
| Plaintext format and charset | | | |
| Transform order | | | |
| Algorithm/mode/padding | | | |
| Key source and role | | | |
| IV/nonce/tag/signature source | | | |
| Ciphertext layout and outer encoding | | | |
| Client implementation and call site | | | |

Express each direction as a compact formula, for example:

```text
wire_request = encode(frame(encrypt(serialize(request), request_context)))
response = deserialize(decrypt(unframe(decode(wire_response)), response_context))
```

Include extracted secrets by reference or redacted fingerprint by default. Separate facts, assumptions, and unresolved questions.

### 4. Prove compatibility before proxying

Build the smallest local harness that invokes the original client implementation when practical. Verify in this order:

1. Decode a captured ciphertext to the expected plaintext.
2. Encrypt known plaintext and decrypt it with the peer implementation.
3. Test Unicode, empty bodies, binary data, and realistic payload sizes.
4. Test tampering to confirm authentication or signature behavior.
5. Confirm nonce/IV uniqueness and exact framing.

Prefer the original runtime/library when cross-language behavior differs. Do not compensate for a failed vector with unverified prefix stripping or mode changes.

### 5. Choose the interception design

Use the least invasive design that preserves protocol semantics:

- **Single proxy:** use when one process can decrypt inbound payloads and re-encrypt outbound payloads for both peers.
- **Two-sided proxy:** place the inspection tool between a client-side decrypt/re-encrypt adapter and a server-side re-encrypt/decrypt adapter when each peer must retain its original wire contract.
- **Runtime instrumentation:** use when ephemeral secrets, device-bound keys, anti-tamper logic, or native code make static replacement unreliable.
- **Client asset patching:** use only when a replaceable public key or configuration value is delivered to the client. Patch exact verified occurrences and handle caching, compression, integrity attributes, CSP, and source maps.

Keep cryptography behind an adapter interface such as `detect`, `decode`, `decrypt`, `encrypt`, `encode`, and `validate`. Keep host/path filtering, flow correlation, and proxy hooks algorithm-neutral.

### 6. Implement defensively

- Restrict processing to explicit hosts, paths, methods, and content types.
- Preserve headers and update content length/encoding after body changes.
- Skip empty bodies and static assets unless intentionally patching them.
- Correlate response handling with per-flow state instead of guessing from body shape.
- Fail closed for transformations: log a redacted diagnostic and pass through or stop according to the user's test plan.
- Never reuse nonces or IVs where uniqueness is required.
- Keep secrets outside source code and redact logs.
- Make startup validate configuration and known test vectors before listening.

### 7. Verify end to end

Demonstrate all four legs: client-to-adapter ciphertext, plaintext at the inspection point, adapter-to-server ciphertext, and the symmetric response path. Confirm untouched traffic remains byte-equivalent where expected. Test cache misses, retries, errors, redirects, chunked/compressed bodies, concurrency, and process restarts.

Deliver:

1. Evidence matrix and directional formulas.
2. Architecture and trust-boundary explanation.
3. Minimal configuration and startup commands.
4. Tested implementation or implementation plan.
5. Verification results and a troubleshooting table keyed to observable symptoms.

