# Security Policy

## Scope

PythonShenanigans is a local, offline library. It makes no network calls, has no
code-evaluation (`eval`/`exec`) anywhere, and its only I/O is the strings you
hand it.

## Untrusted character codes

A character code from someone else should be treated as untrusted input.

- **No decompression-size limit.** Decoding runs zstd over attacker-controlled
  bytes with no cap on the output size. zstd frames are highly compressible, so
  a short code can expand into a very large payload and exhaust memory. There is
  currently no limit; decode only codes you trust, or wrap
  `pythonshenanigans.codec.decode` in your own size/time guard.
- **Malicious movesets are a game-level risk, not a library-level one.** The
  library faithfully preserves whatever a payload contains, including skills
  that are disruptive in-game. Only load codes you generated or reviewed.

Codes *you* generate are safe to round-trip: the library preserves every field,
including ones it does not model.

## Reporting

Open an issue at <https://github.com/dnd-ed/pythonshenanigans/issues>. For
anything you consider sensitive, contact the maintainers privately first.
