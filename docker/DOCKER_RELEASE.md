# DISCOVER Docker Support

## Overview

This release adds production-ready Docker support for DISCOVER, enabling containerized deployment with full GPU acceleration, TLS/HTTPS support, and module isolation.

## Prerequisites

Before using DISCOVER with Docker, ensure you have:

**Required:**
- **Docker Engine 20.10+** or **Docker Desktop**
- **Docker Compose V2** (plugin version - verify with `docker compose version`)

**Optional (for GPU acceleration):**
- **NVIDIA Container Toolkit** (required for ML modules with GPU)
- **NVIDIA GPU drivers** on host machine

See README.md for detailed installation instructions for your platform.

## What's New

### Docker Containerization
- **PyPI Installation**: Docker image installs `hcai-discover` from PyPI
- **NVIDIA CUDA**: GPU support via `nvidia/cuda:12.9.1-runtime-ubuntu24.04` base image
- **Python 3.12**: Native support on Ubuntu 24.04
- **Virtual Environment Isolation**: Preserves DISCOVER's module venv architecture
- **TLS/HTTPS**: Dynamic self-signed certificate generation in entrypoint script
- **Rootless Compatible**: UID/GID mapping for proper file permissions

### Key Features

#### 1. GPU Acceleration
- Automatic NVIDIA GPU passthrough
- Supports all CUDA-compatible ML frameworks (PyTorch, TensorFlow, etc.)
- Verified with CUDA 12.9

#### 2. Flexible Volume Mounting
- Separate `HOST_*` variables for volume mount paths
- Support for both relative and absolute paths
- Network drive mounting for large datasets
- Persistent cache for module venvs (~71GB+)

#### 3. Port Configuration
- `HOST_PORT`: External port for browser access (user-configurable)
- `DISCOVER_PORT`: Internal container port (fixed at 8080)
- Docker handles port mapping automatically

#### 4. Security
- TLS/HTTPS with self-signed certificates (auto-generated)
- Option to mount custom certificates
- Non-root container execution via UID/GID mapping

#### 5. Dependencies
Complete system dependencies for ML workloads:
- FFmpeg for video processing
- Build tools (gcc, g++, make) for compiling Python wheels
- pkg-config and libav* libraries for PyAV
- OpenSSL for certificate generation

## Verified Functionality

### Successfully Tested Modules
1. **WhisperX** (v1.0.7)
   - Speech recognition and transcription
   - GPU-accelerated inference
   - PyAV audio processing

2. **BlazeFace**
   - Face detection
   - GPU-accelerated processing

### Test Environment
- **Host OS**: Ubuntu Linux (kernel 6.14.0)
- **Docker**: Docker Compose V2 (v5.0.0)
- **GPU**: NVIDIA GPU with CUDA 12.9
- **Dataset**: Network-mounted Nova database
- **Modules**: Git-cloned discover-modules repository

## File Structure

```
discover/
├── docker/
│   ├── Dockerfile                  # Main image definition
│   ├── docker-compose.yml          # Production configuration
│   ├── docker-compose.example.yml  # Annotated example
│   ├── docker-entrypoint.sh        # Startup script (cert generation)
│   ├── .env.docker.example         # Environment template
│   ├── .dockerignore               # Build context filter
│   ├── setup.sh                    # Automated setup script
│   └── DOCKER_RELEASE.md           # This file
├── README.md                       # Updated with Docker section
└── CLAUDE.md                       # Updated with Docker commands
```

## Quick Start

```bash
# Navigate to project
cd /path/to/discover

# Run automated setup
cd docker
./setup.sh

# Clone modules
cd ..
git clone https://github.com/hcmlab/discover-modules.git cml

# Configure environment
cd docker
cp .env.docker.example .env
# Edit .env with your paths and UID/GID

# Build and start
docker compose build
docker compose up -d

# Access DISCOVER
# If HTTP: http://localhost:8080
# If HTTPS: https://localhost:8080
```

## Configuration Variables

### Required in .env
```bash
# User permissions (rootless Docker)
UID=1000                    # Your user ID (run: id -u)
GID=1000                    # Your group ID (run: id -g)

# Host port (browser access)
HOST_PORT=8080              # Or your custom port

# Volume mount paths (HOST machine)
HOST_CACHE_DIR=../cache     # Module venvs and model weights
HOST_CML_DIR=../cml         # ML modules source
HOST_DATA_DIR=../data       # Datasets (read-write)
HOST_LOG_DIR=../log         # Job logs
HOST_TMP_DIR=../tmp         # Temporary files

# Server configuration
DISCOVER_USE_TLS=false      # Enable HTTPS

# Backend options
DISCOVER_BACKEND=venv
DISCOVER_VIDEO_BACKEND=IMAGEIO
VENV_FORCE_UPDATE=False
VENV_LOG_VERBOSE=True

# Optional: PyTorch CUDA index URLs
VENV_EXTRA_INDEX_URLS=https://download.pytorch.org/whl/cu129
```

### Set by docker-compose.yml (Container-side)
```bash
DISCOVER_HOST=0.0.0.0       # Listen on all interfaces
DISCOVER_PORT=8080          # Internal container port
DISCOVER_CML_DIR=/app/cml   # Container paths
DISCOVER_DATA_DIR=/app/data
DISCOVER_CACHE_DIR=/app/cache
DISCOVER_LOG_DIR=/app/log
DISCOVER_TMP_DIR=/app/tmp
```

## Architecture Decisions

### 1. PyPI Installation vs Source Build
**Decision**: Install from PyPI
**Rationale**:
- Simplifies Dockerfile
- Users get stable releases
- Faster build times
- Easier version management

### 2. Base Image: NVIDIA CUDA
**Decision**: `nvidia/cuda:12.9.1-runtime-ubuntu24.04`
**Rationale**:
- GPU support out-of-the-box
- Ubuntu 24.04 has Python 3.12 by default
- Runtime variant keeps image size manageable
- Compatible with all CUDA ML frameworks

### 3. Virtual Environment Preservation
**Decision**: Keep module venv isolation
**Rationale**:
- Prevents dependency conflicts between modules
- Fast startup (venvs cached in volume)
- Matches local development workflow
- Module independence

### 4. Separate HOST_* Variables
**Decision**: Separate variables for host paths vs container paths
**Rationale**:
- Volume mounts need host paths
- DISCOVER needs container paths
- Supports network drives with absolute paths
- Clear separation of concerns

### 5. Healthcheck Disabled for TLS
**Decision**: Disable Docker healthcheck when TLS enabled
**Rationale**:
- Docker HEALTHCHECK has issues accessing runtime env vars
- Self-signed certs complicate health verification
- Users can monitor via logs and manual testing
- Doesn't affect container stability

### 6. tmpfs → Volume Mount for /app/tmp
**Decision**: Use regular volume mount instead of tmpfs
**Rationale**:
- tmpfs permission issues with non-root users
- Easier debugging (can inspect temp files)
- Files persist if needed for investigation
- No performance penalty for temp file use case

## Known Issues & Limitations

### 1. Healthcheck with TLS
- Docker healthcheck disabled when `DISCOVER_USE_TLS=true`
- Workaround: Monitor via `docker compose logs -f`
- Future: Investigate healthcheck script with proper env var access

### 2. Image Size
- ~4-5GB due to CUDA runtime and ML dependencies
- Trade-off for GPU support and build tools
- Future: Consider multi-stage build for optimization

### 3. First Module Run
- First execution of a module installs requirements
- Can take several minutes depending on dependencies
- Subsequent runs are fast (venv cached)
- Expected behavior, not a bug

## Troubleshooting

### Permission Denied Errors
```bash
# Ensure UID/GID match your user
echo "UID=$(id -u)" >> .env
echo "GID=$(id -g)" >> .env

# Check volume directory ownership
ls -la ../cache ../log ../tmp

# Fix if needed
sudo chown -R $(id -u):$(id -g) ../cache ../log ../tmp
```

### GPU Not Detected
```bash
# Verify NVIDIA drivers on host
nvidia-smi

# Test Docker GPU access
docker run --rm --gpus all nvidia/cuda:12.9.1-runtime-ubuntu24.04 nvidia-smi

# Check NVIDIA Container Toolkit installed
dpkg -l | grep nvidia-container-toolkit
```

### Module Installation Failures
```bash
# Check if module venv has errors
docker compose exec discover ls -la /app/cache/venvs/

# View detailed logs
docker compose logs discover | grep -A10 "Installing"

# Force venv recreation
# In .env: VENV_FORCE_UPDATE=True
docker compose restart
```

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8080

# Change HOST_PORT in .env
# Or stop conflicting service
```

### Cannot Access HTTPS
```bash
# Accept self-signed certificate in browser
# Or use curl with -k flag
curl -k https://localhost:8080

# For production, mount custom certificates:
# docker-compose.yml volumes:
#   - ./certs/cert.pem:/app/certs/cert.pem:ro
#   - ./certs/key.pem:/app/certs/key.pem:ro
```

## Performance Notes

### Storage Requirements
- **Base Image**: ~2GB (CUDA runtime)
- **DISCOVER + Python deps**: ~500MB
- **Module venvs**: ~71GB+ (varies by modules used)
- **Model weights**: Varies (cached in HOST_CACHE_DIR)
- **Total**: Plan for 100GB+ for HOST_CACHE_DIR

### Network Drives
Successfully tested with:
- SMB/CIFS network shares
- NFS mounts
- Mixed local (cache/log) + network (data) paths

Tips:
- Use absolute paths for network drives
- Ensure network mount available before docker compose up
- Consider local cache for better performance

## Future Enhancements

### Optimization
- Multi-stage build to reduce image size
- Pre-built module venvs for common modules
- Slim variant without GPU support

### Features
- Docker Swarm / Kubernetes support
- Health check fix for TLS deployments
- Pre-commit hooks for Dockerfile linting
- Automated testing in CI/CD

## Migration from Local Install

If you're currently running DISCOVER locally:

```bash
# 1. Backup your local setup
cp -r cache cache.backup
cp .env .env.backup

# 2. Move to Docker setup
cd docker
./setup.sh

# 3. Configure volumes to point to existing data
# In .env:
HOST_CACHE_DIR=../cache  # Reuse existing cache
HOST_DATA_DIR=/mnt/datasets/nova/data  # Your existing data

# 4. Build and start
docker compose build
docker compose up -d

# 5. Verify modules work
docker compose logs -f
```

Your existing module venvs will be reused, no reinstallation needed!

## Support

For issues related to:
- **Docker setup**: Check this document and README.md
- **Module errors**: Check discover-modules repository
- **DISCOVER core**: Check main repository issues

## Contributors

Docker implementation developed and tested by the DISCOVER team.

Special thanks to early testers and the community for feedback.

## License

Same as DISCOVER main project.
