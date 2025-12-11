# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management
- **Install in development mode**: `pip install -e .`
- **Build package**: `python -m build`
- **Install from PyPI**: `pip install hcai-discover`

### Running the Application
- **Start DISCOVER server**: `discover`
- **Run with custom config**: `discover --host 0.0.0.0 --port 8080 --cml_dir "/path/to/cml" --data_dir "/path/to/data"`
- **Run from source**: `python -m discover.app`

### Documentation
- **Build docs**: `make html` (from `docs/` directory)
- **Windows**: `make.bat html` (from `docs/` directory)

### Environment Setup
- **Create venv**: `python -m venv discover-venv`
- **Activate**: `source discover-venv/bin/activate` (Linux/macOS) or `discover-venv\Scripts\activate` (Windows)

### Docker Commands
All Docker files are located in the `docker/` subdirectory. Run commands from there.

**Important:** Use `docker compose` (V2 with space), not `docker-compose` (V1 with hyphen).

**Quick Start:**
```bash
cd docker
./setup.sh                    # Automated setup
cd .. && git clone https://github.com/hcmlab/discover-modules.git cml
cd docker
# Edit .env with your UID/GID and paths
docker compose build
docker compose up -d
```

**Common Commands:**
- **Build image**: `docker compose build`
- **Start services**: `docker compose up -d`
- **View logs**: `docker compose logs -f`
- **Stop services**: `docker compose down`
- **Rebuild**: `docker compose build --no-cache && docker compose up -d`
- **Clean up (removes volumes)**: `docker compose down -v`
- **Create .env**: `cp .env.docker.example .env` (then edit with your settings)
- **Shell access**: `docker compose exec discover bash`
- **GPU test**: `docker compose exec discover nvidia-smi`

**Configuration:**
- Docker images install DISCOVER from PyPI, not from source
- Specify version in `.env`: `DISCOVER_VERSION=1.1.0` or `DISCOVER_VERSION=latest`
- Set `HOST_PORT` for custom browser access port
- Use `HOST_*` variables for volume mount paths (host machine)
- Container always uses `/app/*` paths internally

**Verified Modules:**
- WhisperX (speech recognition)
- BlazeFace (face detection)
- GPU acceleration with CUDA 12.9
- TLS/HTTPS with self-signed certificates

## Architecture Overview

DISCOVER is a modular Flask-based web server framework for human behavior analysis that uses virtual environments to run machine learning modules in isolation.

### Core Components

**Main Application** (`discover/app.py`):
- Flask server with multiple route blueprints
- Configurable via command-line args, environment variables, or .env files
- Uses Waitress WSGI server for production serving

**Route Modules** (`discover/route/`):
- `train.py` - Model training endpoints
- `process.py` - Data processing jobs
- `predict.py` - Inference endpoints
- `status.py` - Job status monitoring
- `ui.py` - Web interface routes
- `log.py` - Logging and debugging
- `upload.py` - File upload handling
- `cancel.py` - Job cancellation
- `fetch_result.py` - Result retrieval

**Backend System** (`discover/backend/virtual_environment.py`):
- `VenvHandler` class manages isolated Python environments for each ML module
- Automatically creates/manages virtual environments in `cache/venvs/`
- Installs module-specific requirements and `hcai-discover-utils`
- Runs Python scripts and shell commands within activated environments

**Execution Layer** (`discover/exec/execution_handler.py`):
- Orchestrates job execution across different backend types
- Manages job lifecycle, logging, and resource cleanup

**Utilities** (`discover/utils/`):
- `venv_utils.py` - Virtual environment path/command utilities
- `job_utils.py` - Job management helpers
- `log_utils.py` - Logging configuration
- `env.py` - Environment variable definitions

### Key Architecture Patterns

1. **Modular Design**: Each ML module lives in separate directory with its own `requirements.txt`
2. **Isolation**: Virtual environments prevent dependency conflicts between modules
3. **Blueprint Architecture**: Flask routes organized as separate blueprints for clean separation
4. **Configuration Hierarchy**: CLI args > .env file > environment variables > defaults
5. **Async Job Processing**: Long-running ML tasks executed in background with status tracking

### Directory Structure

- `cache/` - Model weights, downloads, and virtual environments
- `cml/` - Cooperative machine learning modules (NOVA integration)
- `data/` - Training/processing data directory
- `log/` - Application and job logging
- `tmp/` - Temporary file storage
- `discover/templates/` - HTML templates for web interface

### Important Notes

- No formal test suite or linting tools are currently configured
- Virtual environments are cached in `cache/venvs/` with naming based on module directory and version
- The system supports multiple video backends (IMAGEIO, DECORD, MOVIEPY, PYAV)
- Jobs can be cancelled mid-execution via process management
- investigate why these packages are falsely tried to be installed on module venv creation:\
2025-08-12 11:24:26 INFO ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
2025-08-12 11:24:26 INFO hcai-discover 1.0.1 requires flask==3.0.0, which is not installed.
2025-08-12 11:24:26 INFO hcai-discover 1.0.1 requires psutil, which is not installed.
2025-08-12 11:24:26 INFO hcai-discover 1.0.1 requires toml, which is not installed.
2025-08-12 11:24:26 INFO hcai-discover 1.0.1 requires waitress, which is not installed.