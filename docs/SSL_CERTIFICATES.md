# SSL Certificate Configuration for Self-Hosted Git Servers

When using Cockpit with self-hosted GitHub or GitLab servers that use custom SSL certificates, you may encounter certificate verification issues. This guide provides several approaches to resolve these issues.

## 🔐 Quick Solutions

### Method 1: Environment Variables (Recommended)

Configure SSL settings in your `.env` file:

```bash
# For self-signed or custom CA certificates
GIT_SSL_VERIFY=false  # Temporary solution - not recommended for production

# Or configure custom CA certificate (recommended)
GIT_SSL_VERIFY=true
GIT_SSL_CA_INFO=/path/to/your/custom-ca-cert.pem

# For client certificate authentication (if required)
GIT_SSL_CERT=/path/to/your/client-cert.pem
```

### Method 2: Docker Volume Mounting

For Docker deployments, mount your certificate files:

```yaml
# docker-compose.yml
services:
  cockpit:
    volumes:
      - ./certificates:/app/certificates:ro
    environment:
      - GIT_SSL_CA_INFO=/app/certificates/ca-cert.pem
```

## 🛠️ Detailed Configuration Options

### Option 1: Add CA Certificate to System Trust Store (Best Practice)

**Ubuntu/Debian:**
```bash
# Copy your CA certificate
sudo cp your-ca-cert.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# Restart Cockpit containers
docker-compose restart
```

**CentOS/RHEL:**
```bash
sudo cp your-ca-cert.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust
```

**macOS:**
```bash
sudo security add-trusted-cert -d root -r trustRoot \
  -k /System/Library/Keychains/SystemRootCertificates.keychain \
  your-ca-cert.crt
```

### Option 2: Application-Level Configuration

Configure in your environment file:

```bash
# .env or .env.docker
GIT_SSL_VERIFY=true
GIT_SSL_CA_INFO=/path/to/ca-bundle.pem
```

### Option 3: Git Global Configuration

Set Git configuration globally (affects all Git operations):

```bash
# For specific host only (recommended)
git config --global http."https://your-gitlab.company.com/".sslVerify false
git config --global http."https://your-gitlab.company.com/".sslCAInfo /path/to/ca-cert.pem

# Or globally (not recommended)
git config --global http.sslVerify false
```

## 🐳 Docker-Specific Solutions

### Mount Certificate Directory

```yaml
# docker-compose.yml
version: '3.8'
services:
  cockpit:
    build: .
    volumes:
      - ./certs:/etc/ssl/certs/custom:ro
    environment:
      - GIT_SSL_CA_INFO=/etc/ssl/certs/custom/ca-cert.pem
      - GIT_SSL_VERIFY=true
```

### Build Custom Image with Certificates

```dockerfile
# Dockerfile.custom
FROM your-cockpit-image

# Copy CA certificate
COPY ca-cert.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Set environment variables
ENV GIT_SSL_VERIFY=true
```

## ⚠️ Security Considerations

### ✅ Recommended Approaches
1. **Add CA certificate to system trust store**
2. **Use `GIT_SSL_CA_INFO` with custom CA certificate**
3. **Configure per-host SSL settings**

### ❌ Not Recommended for Production
1. **Setting `GIT_SSL_VERIFY=false`** - Disables all SSL verification
2. **Global SSL verification disable** - Affects all Git operations

## 🧪 Testing Your Configuration

### Test Git Connectivity

```bash
# Test from command line
git ls-remote https://your-gitlab.company.com/user/repo.git

# Test with custom CA
GIT_SSL_CA_INFO=/path/to/ca-cert.pem git ls-remote https://your-gitlab.company.com/user/repo.git

# Test without SSL verification (debugging only)
GIT_SSL_NO_VERIFY=1 git ls-remote https://your-gitlab.company.com/user/repo.git
```

### Test from Cockpit

1. Configure your Git settings in Cockpit Settings page
2. Use the "Test Connection" button
3. Check backend logs for SSL-related errors

## 🔧 Troubleshooting

### Common SSL Errors

**Error:** `SSL certificate problem: self signed certificate`
```bash
# Solution: Add CA certificate or disable verification
GIT_SSL_CA_INFO=/path/to/ca-cert.pem
```

**Error:** `SSL certificate problem: unable to get local issuer certificate`
```bash
# Solution: Ensure complete certificate chain
# Make sure your ca-cert.pem includes all intermediate certificates
```

**Error:** `SSL certificate problem: certificate verify failed`
```bash
# Debug: Check certificate details
openssl s_client -connect your-gitlab.company.com:443 -servername your-gitlab.company.com

# Temporary workaround for testing
GIT_SSL_VERIFY=false
```

### Debugging Commands

```bash
# Check Git SSL configuration
git config --list | grep ssl

# Test SSL connection
openssl s_client -connect your-server.com:443 -verify_return_error

# Check certificate chain
curl -vI https://your-server.com

# Test with custom CA
curl --cacert /path/to/ca-cert.pem https://your-server.com
```

## 📝 Example Configurations

### Self-Signed Certificate Example

```bash
# .env
GIT_SSL_VERIFY=false  # Only for development/testing
```

### Custom CA Certificate Example

```bash
# .env
GIT_SSL_VERIFY=true
GIT_SSL_CA_INFO=/app/certificates/company-ca.pem
```

### Client Certificate Authentication Example

```bash
# .env
GIT_SSL_VERIFY=true
GIT_SSL_CA_INFO=/app/certificates/ca-cert.pem
GIT_SSL_CERT=/app/certificates/client-cert.pem
```

## 🔗 Additional Resources

- [Git SSL Configuration Documentation](https://git-scm.com/docs/git-config#Documentation/git-config.txt-httpsslCAInfo)
- [OpenSSL Certificate Verification](https://www.openssl.org/docs/man1.1.1/man1/verify.html)
- [Docker Secrets Management](https://docs.docker.com/engine/swarm/secrets/)

---

**Note:** Always prefer proper certificate chain configuration over disabling SSL verification for production environments.
