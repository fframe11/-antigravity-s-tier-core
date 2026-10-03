---
name: dns-ssl-management
description: Use when configuring DNS records, SSL/TLS certificates, domain routing, CDN setup, or managing Cloudflare/Route53/Google Cloud DNS. Covers cert automation with Let's Encrypt, ACME, and cloud-native certificate managers.
---

# DNS & SSL/TLS Management Guide

This skill governs domain name resolution, record architecture, edge routing, and automated TLS/SSL certificate lifecycles across cloud providers, CDN proxies, and Kubernetes clusters.

## When to Use This Skill
- Configuring authoritative DNS zones, delegations, and records in Cloudflare, AWS Route 53, or Google Cloud DNS.
- Automating TLS certificate provisioning, SAN multi-domain certs, and wildcards using Let's Encrypt and the ACME protocol.
- Deploying and troubleshooting `cert-manager` inside Kubernetes clusters (Ingress-NGINX, Gateway API).
- Setting up CDN proxy layers (Cloudflare Orange-Cloud vs. Grey-Cloud), origin encryption, and HSTS headers.
- Diagnosing DNS propagation delays, split-horizon DNS conflicts, and SSL handshake errors (`ERR_SSL_VERSION_OR_CIPHER_MISMATCH`, `SSL_ERROR_NO_CYPHER_OVERLAP`).
- Securing domains against rogue certificate issuance using CAA records and monitoring Certificate Transparency (CT) logs.

---

## Core Principles & Guidelines

### 1. DNS Record Architecture & TTL Strategy
- **A / AAAA Records**: Direct mapping to IPv4 / IPv6 addresses. Never map edge-cached origins directly if behind a CDN.
- **CNAME Records**: Canonical aliases. RFC 1034 restricts CNAME on domain apex (`@` / `example.com`). Use **CNAME flattening / ALIAS / ANAME** at apex when supported by DNS providers (Cloudflare, Route 53 ALIAS).
- **MX Records**: Mail exchangers with priority values (lower integer = higher priority). MX target must be an A/AAAA record, never a CNAME.
- **TXT Records**: Used for identity and validation (SPF, DKIM, DMARC, ACME challenge tokens, site ownership).
- **SRV Records**: Service locator specifying port, priority, weight, and target host (SIP, LDAP, service discovery).
- **CAA Records**: Restrict which Certificate Authorities (CAs) can issue certificates for the domain and subdomains.
- **TTL Lifecycle**: Normal (3600s–86400s); Pre-Migration cutover (60s–300s set 24h prior); Cloudflare proxied (automatic).

### 2. ACME Challenge Protocols
- **HTTP-01 Challenge**: Verifies domain ownership via port 80 at `http://<domain>/.well-known/acme-challenge/<token>`.
  - *Constraint*: Cannot issue wildcard certificates (`*.example.com`). Origin firewall must allow inbound HTTP on port 80 during validation.
- **DNS-01 Challenge**: Verifies domain ownership by writing a TXT record at `_acme-challenge.<domain>`.
  - *Requirement*: Mandatory for wildcard certificates and internal/air-gapped services without public inbound access. Requires programmatic DNS API credentials.

### 3. Cloudflare Proxy & SSL Modes
- **Off / Flexible**: INSECURE. Flexible encrypts browser-to-Cloudflare but uses plaintext HTTP to the origin. Prone to infinite redirect loops (301) and man-in-the-middle attacks.
- **Full**: Encrypted edge-to-origin, but accepts self-signed or invalid origin certs.
- **Full (Strict)**: PRODUCTION MANDATE. Validates origin certificate chain against a trusted CA (or Cloudflare Origin CA).
- **Edge Certificates**: Managed automatically by Cloudflare edge; origin certificates handle backend encryption.

### 4. Defense-in-Depth & Certificate Hardening
- **HSTS (HTTP Strict Transport Security)**: Enforce HTTPS at browser level. Include `includeSubDomains` and `preload` only after verifying all subdomains support TLS.
- **Certificate Transparency (CT)**: All public CAs publish certificates to public append-only logs. Monitor CT logs (e.g., via Certstream or crt.sh) to detect rogue certificates immediately.

---

## Implementation Patterns with Concrete Examples

### Pattern 1: DNS Baseline with Apex Flattening & CAA (Terraform / Route 53 / Cloudflare)
```hcl
# CAA Records restricting cert issuance to Let's Encrypt with violation reporting
resource "cloudflare_record" "caa_issue" {
  zone_id = var.cloudflare_zone_id
  name    = "@"
  type    = "CAA"
  data    = { flags = "0", tag = "issue", value = "letsencrypt.org" }
}
resource "cloudflare_record" "caa_wildcard" {
  zone_id = var.cloudflare_zone_id
  name    = "@"
  type    = "CAA"
  data    = { flags = "0", tag = "issuewild", value = "letsencrypt.org" }
}
resource "cloudflare_record" "caa_iodef" {
  zone_id = var.cloudflare_zone_id
  name    = "@"
  type    = "CAA"
  data    = { flags = "0", tag = "iodef", value = "mailto:security@example.com" }
}
```

### Pattern 2: Automated Wildcard Certificate with Let's Encrypt & Certbot (DNS-01)
```bash
# Install certbot with Cloudflare DNS plugin and request wildcard SAN cert
sudo apt-get install -y certbot python3-certbot-dns-cloudflare
sudo certbot certonly \
  --dns-cloudflare --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
  --dns-cloudflare-propagation-seconds 30 \
  -d example.com -d "*.example.com" --agree-tos -m admin@example.com --non-interactive

# Test automated renewal with dry-run
sudo certbot renew --dry-run
```

### Pattern 3: Kubernetes cert-manager with DNS-01 and Ingress
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-production
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: devops@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    solvers:
    - dns01:
        cloudflare:
          apiTokenSecretRef:
            name: cloudflare-api-token-secret
            key: api-token
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-production
spec:
  ingressClassName: nginx
  tls:
  - hosts: [api.example.com, "*.api.example.com"]
    secretName: api-example-tls-secret
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port: { number: 8080 }
```

### Pattern 4: NGINX TLS 1.3 Hardening & HSTS Configuration
```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 1.1.1.1 8.8.8.8 valid=300s;

    # HSTS (2 years, subdomains, preload)
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

### Pattern 5: DNS Resolution & TLS Troubleshooting Commands
```bash
# Trace authoritative DNS delegation from root servers
dig +trace example.com

# Query specific nameservers directly bypassing local cache
dig @1.1.1.1 example.com A +nocmd +noall +answer

# Inspect CAA records
dig example.com CAA +short

# Verify SSL certificate chain and expiration over network
openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null 2>/dev/null | openssl x509 -noout -dates -subject -issuer

# Test OCSP stapling response
openssl s_client -connect example.com:443 -status -tlsextdebug < /dev/null 2>&1 | grep -i "OCSP response"
```

---

## Anti-Patterns to Avoid
- **Using CNAME on Root Apex without Flattening**: Violates RFC 1034 Section 3.6.2. Overwrites NS, SOA, and MX records, dropping all inbound domain emails and breaking nameserver delegation.
- **Cloudflare "Flexible" SSL Mode**: Causes infinite 301 redirect loops if origin has HTTPS redirect enabled, and transmits sensitive credentials unencrypted over the open internet.
- **Attempting HTTP-01 for Wildcards**: Let's Encrypt and ACME RFC 8555 reject HTTP-01 challenges for `*.domain.com`. Always use DNS-01 for wildcards.
- **Blocking Port 80 When HTTPS is Enforced**: Let's Encrypt HTTP-01 challenges hit port 80 first before following redirects. Blocking port 80 breaks certificate renewals.
- **Premature HSTS Preloading**: Once a domain is submitted to the HSTS preload list, browsers hardcode HTTPS connections. Any legacy non-HTTPS subdomain becomes permanently unreachable for visitors.
- **Unmonitored 90-Day Certificates**: Relying on manual renewal reminders. Certbot/cert-manager should renew automatically when 30 days remain (using cron or systemd timer twice daily with random jitter).

---

## Verification Checklist
- [ ] Root apex (`@`) uses A/AAAA records or CNAME flattening (ALIAS); no raw CNAME at apex.
- [ ] CAA records are set to authorize intended CAs (`issue "letsencrypt.org"`, `issuewild "letsencrypt.org"`) and block unauthorized CAs.
- [ ] ACME automated renewal runs dry-run test (`certbot renew --dry-run` or cert-manager `Certificate` condition is `Ready=True`).
- [ ] Cloudflare SSL/TLS encryption mode is set to **Full (Strict)**.
- [ ] HTTP-to-HTTPS redirect returns HTTP 301/308 across all domain aliases.
- [ ] TLS 1.0 and 1.1 are disabled; TLS 1.2 and 1.3 are enabled with secure forward-secrecy cipher suites.
- [ ] OCSP Stapling is enabled and verified via `openssl s_client -status`.
- [ ] HSTS header is active with appropriate `max-age`, evaluated cautiously before adding `preload`.
- [ ] DNS TTL was reduced prior to any scheduled server or cloud IP migration.
