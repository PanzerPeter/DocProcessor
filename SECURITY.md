# Security Policy

## Reporting a Vulnerability

Do **not** open a public GitHub issue for security vulnerabilities.

Email: insgraphizm@gmail.com  
Subject line: `[DocProcessor] Security vulnerability`

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

You will receive a response within 72 hours. Please allow time to patch before public disclosure.

## Scope

| In scope | Out of scope |
|----------|-------------|
| API key exposure | Third-party dependencies' own vulnerabilities |
| PII leakage from extracted text | Tesseract or PyMuPDF upstream bugs |
| Prompt injection via document content | Social engineering |
| Path traversal in file handling | |

## Known Risks

- **Document content sent to Anthropic API**: extracted text (up to 8000 chars) is sent to Anthropic's servers for categorization. Do not process documents containing secrets you do not want transmitted externally.
- **Tesseract**: Tesseract processes untrusted image data. Keep it updated via your system package manager.
