# Security Checklist

- Do NOT commit `.env` or any secrets to source control.
- Use a secrets manager for production (GitHub Secrets, Vault, AWS Secrets Manager).
- Ensure HTTPS on all web endpoints; use Let's Encrypt or managed TLS.
- Verify Stripe webhook signatures (already implemented) and restrict IPs if possible.
- Run dependency checks (`pip-audit`, `safety`) regularly.
- Rotate keys periodically and revoke unused tokens.
- Restrict database access with network rules and strong credentials.
