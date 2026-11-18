# Security Policy

## Supported Versions

Because `pythonshenanigans` is actively developed, security updates and bug fixes are generally applied only to the latest release.

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| Older   | :x:                |

## Untrusted Character Codes

A character code is arbitrary input, so treat codes from other people as untrusted.

* **No decompression-size limit.** Decoding runs zstd over attacker-controlled bytes with no cap on the output size. zstd frames are highly compressible, so a short code can expand into a very large payload and exhaust memory. There is currently no limit — decode only codes you trust, or wrap `pythonshenanigans.codec.decode` in your own size/time guard.
* **Malicious movesets are a game-level risk, not a library-level one.** The library faithfully preserves whatever a payload contains, including skills that are disruptive in-game. Only load codes you generated or reviewed.

Codes *you* generate are safe to round-trip: every field is preserved, including ones the library does not model.

## Reporting a Vulnerability

We take the security of `pythonshenanigans` seriously. If you discover a security vulnerability (such as unsafe deserialization, arbitrary code execution when loading moveset files, or dependency issues), please report it responsibly.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please contact us directly through one of the following private channels:
* **Telegram:** [@itzdanti](https://t.me/itzdanti) *(fastest response)*
* **Email:** [dnd@itzdanti.dev](mailto:dnd@itzdanti.dev)

### What to Include
To help us triage and resolve the issue quickly, please include as much of the following information as possible:
* A clear description of the vulnerability and its potential impact.
* Step-by-step instructions or a minimal Python script to reproduce the issue.
* Sample moveset data or payloads (if applicable).
* The version of `pythonshenanigans` and Python you are using.

### Response Timeline
* **Acknowledgment:** You should receive an acknowledgment of your report within **48–72 hours** (often sooner via Telegram).
* **Updates:** We will keep you informed as we investigate and work on a fix.
* **Disclosure:** Once a patch is released, we will coordinate with you on public disclosure and credit you in the release notes (unless you prefer to remain anonymous).
