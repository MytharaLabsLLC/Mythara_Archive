# Mythara Engine — Installation Guide

**Version:** 1.0.0  
**Platform Support:** Linux (Ubuntu 20.04+, RHEL 8+), Windows Server 2019+, macOS 12+

---

## Prerequisites

### Required Software

- **Docker** 20.10+ (for container deployment)
- **Python** 3.11+ (for native deployment)
- **GPG** 2.x (for signature verification)
- **Git** 2.x (for cloning repository)

### System Requirements

**Minimum:**
- 4 CPU cores
- 8 GB RAM
- 20 GB disk space

**Recommended (Production):**
- 8+ CPU cores
- 16+ GB RAM
- 50+ GB SSD storage

---

## Installation Methods

### Method 1: Docker Container (Recommended)

#### Step 1: Verify Package Integrity

```bash
# Import PGP public key
gpg --import forensic_public_key.asc

# Verify signatures
gpg --verify manifest/RELEASE_MANIFEST.json.asc manifest/RELEASE_MANIFEST.json
gpg --verify manifest/checksums.sha256.asc manifest/checksums.sha256

# Verify file checksums
cd manifest && sha256sum -c checksums.sha256 && cd ..
```

#### Step 2: Build Docker Image

```bash
# Build from Dockerfile
docker build -t mythara-engine:1.0.0 -f core/Dockerfile .

# Verify build
docker images | grep mythara-engine
```

#### Step 3: Run the Validation Suite

The container's default command runs the validation suite:

```bash
# Create output directory
mkdir -p mythara_output

# Run container (validation suite runs automatically)
docker run --rm \
  --name mythara-engine \
  -v $(pwd)/mythara_output:/output \
  -e MYTHARA_ENV=production \
  -e MYTHARA_MANIFEST_REF=ME-archive-0001 \
  mythara-engine:1.0.0
```

#### Step 4: Review Results

```bash
# Check container exited cleanly
docker ps -a | grep mythara-engine

# Review validation reports
ls mythara_output/
```

Validation reports are written to the mounted `/output` directory. Review them before drawing any conclusions about the system's behavior.

---

### Method 2: Native Python Installation

#### Step 1: Clone/Extract Package

```bash
# If from GitHub
git clone https://github.com/your-org/mythara-engine.git
cd mythara-engine

# If from ZIP
unzip mythara-engine-v1.0.0.zip
cd mythara-engine-v1.0.0
```

#### Step 2: Create Virtual Environment

```bash
# Create venv
python3.11 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
.\venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

#### Step 4: Configure Environment

Some components read their settings from environment variables or a `config.yml` file. If the component you are running needs one, create it from the table below — there is no example config shipped in this package.

Set the relevant variables:

- `MYTHARA_MANIFEST_REF`: ME-archive-0001
- `MYTHARA_ENV`: production
- `API_KEY`: <generate a secure key>

#### Step 5: Run the Software

```bash
# Run the full validation suite
python run_validation_suite.py

# Or run the Witnessed Journal prototype (local interface on the emotional chain)
python journal_app/server.py
# Then open http://127.0.0.1:8137 — localhost only, a working prototype, not production
```

---

### Method 3: Air-Gapped/Sovereign Deployment

#### Step 1: Transfer Package

```bash
# Create tarball with dependencies
tar -czf mythara-airgap.tar.gz \
  mythara-engine/ \
  forensic_public_key.asc \
  manifest/ \
  requirements.txt

# Transfer to air-gapped system via approved method
```

#### Step 2: Verify on Air-Gapped System

```bash
# Extract
tar -xzf mythara-airgap.tar.gz
cd mythara-engine/

# Verify signatures (offline)
gpg --import forensic_public_key.asc
gpg --verify manifest/RELEASE_MANIFEST.json.asc manifest/RELEASE_MANIFEST.json
```

#### Step 3: Install Dependencies Offline

```bash
# Option A: Pre-downloaded wheels
pip install --no-index --find-links ./wheels -r requirements.txt

# Option B: Local PyPI mirror
pip install --index-url http://internal-pypi.local/simple -r requirements.txt
```

#### Step 4: Deploy via Docker or Native

Follow Method 1 or Method 2 steps on the air-gapped system.

---

## Configuration

### Environment Variables

These are honored by the container image and by components that read them. Defaults shown are what `core/Dockerfile` sets.

| Variable | Default | Description |
|----------|---------|-------------|
| `MYTHARA_ENV` | `production` (container) / `development` | Environment: `development`, `staging`, `production` |
| `MYTHARA_MANIFEST_REF` | `ME-archive-0001` (container) | Manifest ID for this package |
| `API_PORT` | `8080` | HTTP port, where an HTTP component is in use |
| `LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARN`, `ERROR` |
| `MAX_WORKERS` | `4` | Number of worker processes |
| `ENABLE_AUDIT_LOG` | `true` | Enable audit chain logging |

### Configuration File (config.yml)

```yaml
server:
  host: 0.0.0.0
  port: 8080
  workers: 4

security:
  api_key_required: true
  rate_limit: 1000  # requests per hour
  
manifest:
  ref: ME-archive-0001
  verify_checksums: true
  
logging:
  level: INFO
  audit_enabled: true
  output_dir: /output/audit
```

---

## Validation Tests

### Run Full Test Suite

```bash
# Determinism tests (3 iterations)
python tests/run_determinism_test.py --iterations 3

# Security validation (1000 probes)
python tests/run_leakage_probes.py --count 1000

# SSIP audit (24-hour check)
python tests/run_ssip_audit.py --interval 24h

# Accessibility validation
python tests/test_accessibility_delivery.py
```

### Expected Results

Each suite writes its report under `tests/output/` (determinism report, leakage probe log, SSIP audit report, accessibility delivery report). Review those reports directly — they state their own pass/fail outcomes and any anomalies. Do not treat a passing local run as a certification of any kind; it is evidence of behavior on this machine, on this day.

---

## Troubleshooting

### Issue: "GPG signature verification failed"

**Cause:** Wrong public key or corrupted download

**Solution:**
```bash
# Re-import public key
gpg --delete-keys "Mythara Engine"
gpg --import forensic_public_key.asc

# Re-verify
gpg --verify manifest/RELEASE_MANIFEST.json.asc manifest/RELEASE_MANIFEST.json
```

### Issue: "Docker build fails"

**Cause:** Network issues or missing dependencies

**Solution:**
```bash
# Build with verbose output
docker build --no-cache -t mythara-engine:1.0.0 -f core/Dockerfile . 2>&1 | tee build.log

# Check build.log for specific error
```

### Issue: "Import error: module not found"

**Cause:** Dependencies not installed or wrong Python version

**Solution:**
```bash
# Verify Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

---

## Evaluation Checklist

- [ ] Signatures verified with GPG
- [ ] Checksums validated
- [ ] Validation suite run and reports reviewed
- [ ] Environment variables configured as needed
- [ ] API keys generated and secured, where an HTTP component is in use
- [ ] Firewall rules configured for any exposed ports
- [ ] Backup strategy considered for chain data

---

## Support

**Questions:**  
Email: mytharalabs@yahoo.com  
Include: what you ran, your environment, and relevant logs

Support terms, where any exist, are defined in a signed licensing agreement — there is no standing SLA on an evaluation package.

---

**Evaluation setup complete.** For the authoritative account of how the system works, read `docs/📖 Mythara Bible Books I–V.md`.
