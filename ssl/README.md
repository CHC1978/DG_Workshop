# SSL Certificates Directory

This directory is for SSL/TLS certificates used by the frontend Nginx container.

## For Production (NAS with Tailscale)

Certificates are generated on the NAS using Tailscale. See `scripts/setup-ssl.md` for instructions.

Required files on NAS:
- `server.crt` - SSL certificate
- `server.key` - Private key
- `https_enabled` - Flag file to enable HTTPS redirect

## For Development (Windows)

Development mode uses HTTP only. No certificates needed.

## Security Note

**DO NOT** commit actual certificate files to Git. The `.gitignore` is configured to exclude:
- `*.crt`
- `*.key`
- `*.pem`
