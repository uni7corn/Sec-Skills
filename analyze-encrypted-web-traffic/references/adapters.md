# Protocol adapter checks

Read only the sections relevant to the observed implementation. Values in client code and captured vectors take precedence over library defaults.

## Symmetric encryption

- Identify AES/SM4/ChaCha family, mode, key length, padding, IV or nonce, authentication tag, and associated data.
- Distinguish encrypt-then-MAC, MAC-then-encrypt, and AEAD.
- Determine whether key material is static, derived, negotiated, or wrapped; capture the KDF, salt, label, and iteration parameters.
- Reproduce the exact field concatenation and canonicalization used for MACs or signatures.

## Asymmetric and hybrid encryption

- For RSA, identify OAEP versus PKCS#1 v1.5, OAEP hash/MGF hash/label, block layout, and whether RSA only wraps a session key.
- For ECIES-like or SM2 encryption, identify curve/domain parameters, point encoding, component order, KDF, digest, and raw versus ASN.1 framing.
- For key agreement, identify ephemeral/static roles, transcript inputs, peer validation, and key-confirmation steps.

## SM2-specific compatibility

- Confirm C1C3C2 versus C1C2C3 from code or vectors rather than assuming a library's numeric `mode` convention.
- Confirm whether the uncompressed point marker `04` is inside or outside the library output.
- Confirm raw versus ASN.1 encoding and public-key representation.
- Validate key ranges and derive the public key from the private key for a consistency check.
- Cross-test the exact browser library against the proxy implementation; similarly named SM2 libraries are not automatically wire-compatible.

## Signatures

- Determine signing input, canonicalization, hash, key identifier, timestamp/nonce rules, and signature encoding.
- For ECDSA/SM2 signatures, distinguish raw `r || s` from DER/ASN.1 and check whether SM2 user identity (`ZA`) participates.
- Decide whether the proxy can recompute signatures with authorized test keys or must instrument the original signer.

## Encodings and envelopes

- Test hex case, standard/Base64URL alphabet, padding, prefixes, length fields, JSON escaping, byte order, and character encoding.
- Determine whether compression occurs before or after encryption.
- Treat a ciphertext detector as a routing hint, not proof; combine endpoint, content type, schema, and successful authenticated decoding.

## Proxy mapping

Map the recovered protocol into these direction-specific operations:

```text
client request:  detect -> decode -> decrypt -> expose plaintext
server request:  serialize -> encrypt for server -> frame -> encode
server response: detect -> decode -> decrypt -> expose plaintext
client response: serialize -> encrypt for client -> frame -> encode
```

Request and response may use different algorithms, keys, envelopes, or signatures. Model them independently before sharing code.
