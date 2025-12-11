# DISCOVER - A Modular Software Framework for Human Behavior Analysis


## Overview

DISCOVER is an open-source software framework designed to facilitate computational-driven data exploration in human behavior analysis. This user-friendly and modular platform streamlines complex methodologies, enabling researchers across disciplines to engage in detailed behavioral analysis without extensive technical expertise.

Key Features

* Modularity: DISCOVER's modular architecture allows for easy integration of new features and customization.
* User-Friendliness: Intuitive interface simplifies the data exploration process, making it accessible to non-technical users.
* Flexibility: Supports a wide range of data types and analysis workflows.
* Scalability: Handles large datasets with ease.

Use Cases

* Interactive Semantic Content Exploration
* Visual Inspection
* Aided Annotation
* Multimodal Scene Search

## Getting Started

DISCOVER provides a set of blueprints for exploratory data analysis, serving as a starting point for researchers to engage in detailed behavioral analysis.

### Prerequesites

Before starting to install DISCOVER you need to install Python and FFMPEG.
DISCOVER is currently developed and tested on:

* Python 3.12.x
* Ubuntu Linux

While other Python versions and operating systems may work, they are not actively tested or supported.

You can download the current version of python for your system [here](https://www.python.org/downloads/).

Download the current version off FFMPEG binaries from [here](https://github.com/BtbN/FFmpeg-Builds/releases) for your system and make sure to extract them to a place that is in your system path.

### Recommended Installation on Windows: Using WSL

For Windows users, we strongly recommend installing DISCOVER using Windows Subsystem for Linux (WSL) instead of native Windows installation. This approach provides better compatibility and avoids common issues with package compilation.

**Setting up WSL:**

1. Install WSL 2 by opening PowerShell as Administrator and running:
   ```
   wsl --install
   ```

2. After installation, open your WSL terminal (Ubuntu or your chosen distribution).

3. Install the required system packages for building the `av` package and its dependencies:
   ```bash
   sudo apt update
   sudo apt install ffmpeg python3-dev build-essential
   ```

4. Install Python (if not already installed):
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```

5. Continue with the Setup instructions below within your WSL environment.

### Virtual Environment Setup

It is recommended to setup a separate virtual environment to isolate the DISCOVER installation from your system python installation.
To do so, open a terminal at the directory where your virtual environment should be installed and paste the following command:

```python -m venv discover-venv```

You can then activate the virtual environment like this:

**Linux/macOS/WSL:**
```source discover-venv/bin/activate```

**Windows (native):**
```.\discover-venv\Scripts\activate```

### Setup

Install DISCOVER using pip like this:

```pip install hcai-discover```

### Start the server

To start DISCOVER you just open a Terminal and type

```discover```

DISCOVER takes the following optional arguments as input:

```
--env: '' : Path to a dotenv file containing your server configuration

--host: 0.0.0.0 : The IP for the Server to listen

--port : 8080 : The port for the Server to be bound to

--cml_dir : cml : The cooperative machine learning directory containing DISCOVER modules (available at: https://github.com/hcmlab/discover-modules)

--data_dir : data : Directory where the data resides

--cache_dir : cache : Cache directory for Models and other downloadable content

--tmp_dir : tmp : Directory to store data for temporary usage

--log_dir : log : Directory to store logfiles.

--use_tls : Enable TLS/SSL for HTTPS connections (requires certificates)
```

Internally DISCOVER converts the input to environment variables with the following names: 

```DISCOVER_HOST```, ```DISCOVER_PORT```, ```DISCOVER_CML_DIR```, ```DISCOVER_DATA_DIR```, ```DISCOVER_CACHE_DIR```, ```DISCOVER_TMP_DIR```, ```DISCOVER_LOG_DIR```, ```DISCOVER_USE_TLS```


All variables can be either passed directly as commandline argument, set in a [dotenv](https://hexdocs.pm/dotenvy/dotenv-file-format.html) file or as system wide environment variables.
During runtime the arguments will be prioritized in this order commandline arguments -> dotenv file -> environment variable -> default value.

If the server started successfully your console output should look like this:
```
Starting DISCOVER v1.0.0...
HOST: 0.0.0.0
PORT: 8080
DISCOVER_CML_DIR : cml
DISCOVER_DATA_DIR : data
DISCOVER_CACHE_DIR : cache
DISCOVER_TMP_DIR : tmp
DISCOVER_LOG_DIR : log
...done
DISCOVER HTTP server starting on 0.0.0.0:8080
```

### Job Management

DISCOVER includes a web-based job management interface accessible at the root URL (e.g., `http://localhost:8080` or `https://localhost:8080` with TLS enabled). This interface allows you to:

* Monitor all running, pending, and completed jobs
* View which module is being used for each job
* Track session progress (e.g., "2/5" sessions completed)
* Cancel running or queued jobs
* Access job logs for detailed information

Jobs that are manually canceled will display a gray "Canceled" button in the Actions column, allowing you to distinguish between naturally failed jobs and those that were canceled by the user.

### Modules

DISCOVER modules contain the machine learning models and processing pipelines. You can get the official modules from:

**https://github.com/hcmlab/discover-modules**

Clone or download the modules repository and set the `--cml_dir` parameter to point to the modules directory.

You can find the full documentation of the project [here](https://hcmlab.github.io/discover).

## Docker Deployment

### Prerequisites

**Required:**
- **Docker Engine 20.10+** or **Docker Desktop**
  ```bash
  # Ubuntu/Debian - Install Docker Engine
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh

  # Add user to docker group (for rootless)
  sudo usermod -aG docker $USER
  newgrp docker
  ```

- **Docker Compose V2** (plugin version - NOT standalone V1)
  ```bash
  # Verify you have V2 (should show v2.x.x)
  docker compose version

  # If you have old v1, remove it
  sudo apt remove docker-compose

  # V2 comes with Docker Engine by default
  # If missing, install docker-compose-plugin
  sudo apt install docker-compose-plugin
  ```

**Optional (for GPU acceleration):**
- **NVIDIA Container Toolkit** (required for ML modules with GPU)
  ```bash
  # Ubuntu/Debian
  distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
  curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
  curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

  sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
  sudo systemctl restart docker

  # Test GPU access
  docker run --rm --gpus all nvidia/cuda:12.9.1-runtime-ubuntu24.04 nvidia-smi
  ```

**Note:** Without NVIDIA Container Toolkit, modules requiring GPU will fall back to CPU (slower).

### Quick Start

**Automated Setup (Recommended):**

```bash
# Run setup script from docker directory
cd docker
./setup.sh

# Clone discover-modules
cd ..
git clone https://github.com/hcmlab/discover-modules.git cml

# Start DISCOVER
cd docker
docker compose up -d
```

**Manual Setup:**

1. **Clone discover-modules repository:**
   ```bash
   git clone https://github.com/hcmlab/discover-modules.git cml
   ```

2. **Navigate to docker directory:**
   ```bash
   cd docker
   ```

3. **Create configuration file:**
   ```bash
   cp .env.docker.example .env
   # Edit .env with your paths and settings
   ```

4. **Set user permissions (for rootless Docker):**
   ```bash
   echo "UID=$(id -u)" >> .env
   echo "GID=$(id -g)" >> .env
   ```

5. **Build and start:**
   ```bash
   docker compose build
   docker compose up -d
   ```

   **Note:** The Docker image installs DISCOVER from PyPI (`hcai-discover`). You can specify a version in `.env`:
   ```bash
   DISCOVER_VERSION=1.1.0  # or "latest" for newest version
   ```

   First build takes ~10-15 minutes to download base image and install dependencies.

6. **Access DISCOVER:**
   - Web interface: http://localhost:8080
   - API endpoints: http://localhost:8080/api/*

### Verified Modules

The Docker deployment has been tested and verified with:
- ✅ **WhisperX** - Speech recognition and transcription
- ✅ **BlazeFace** - Face detection
- ✅ GPU acceleration (NVIDIA CUDA 12.9)
- ✅ TLS/HTTPS with self-signed certificates
- ✅ Module virtual environment isolation
- ✅ Network drive mounting for datasets

### Configuration

See `docker/docker-compose.example.yml` for detailed configuration options.

**Multi-GPU Setup:** See `docker/MULTI_GPU.md` for instructions on:
- Running multiple containers per GPU (e.g., 6 containers on H200 with 144GB VRAM)
- Running one container per GPU for multi-GPU systems
- Load balancing and memory management strategies

#### Volume Mapping

You can use **relative** or **absolute** paths in `docker/.env`:

**Example with mixed paths:**
```bash
# Relative paths (from project root)
DISCOVER_CACHE_DIR=../cache
DISCOVER_LOG_DIR=../log

# Absolute paths (e.g., network drives)
DISCOVER_DATA_DIR=/mnt/datasets/nova/data
DISCOVER_CML_DIR=/home/user/discover-modules/modules
```

**Directory purposes:**
- `cache/` - Module virtual environments and model weights (~71GB+)
- `cml/` - ML module source (clone from discover-modules repo)
- `data/` - Your training/processing datasets (read-write)
- `log/` - Job execution logs

#### GPU Support

DISCOVER automatically uses all available NVIDIA GPUs. To limit GPU usage:

```yaml
# In docker-compose.yml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['0']  # Use only GPU 0
          capabilities: [gpu]
```

**Install NVIDIA Container Toolkit:**
```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

#### HTTPS/TLS

Enable TLS in `.env`:
```bash
DISCOVER_USE_TLS=true
```

**Auto-generated certificates (development):**
DISCOVER will generate self-signed certificates on first start.

**Custom certificates (production):**
Mount your certificates:
```yaml
volumes:
  - ./certs/discover_cert.pem:/app/discover/discover_cert.pem:ro
  - ./certs/discover_key.pem:/app/discover/discover_key.pem:ro
```

### Docker Commands

**Note:** Use `docker compose` (with space) for Docker Compose V2, not `docker-compose` (with hyphen).

```bash
# Build image
docker compose build

# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild after code changes
docker compose up -d --build

# Clean up (removes volumes)
docker compose down -v
```

### Troubleshooting

**"undefined volume" error:**
- Create required directories: `mkdir -p cache cml data log`
- Or use absolute paths in `.env` for directories that don't exist yet

**Permission errors:**
- Ensure UID/GID in .env match your user
- Check volume directory permissions on host
- For network drives, ensure your user has write access

**GPU not detected:**
- Verify NVIDIA drivers: `nvidia-smi`
- Check Docker GPU access: `docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi`

**Port already in use:**
- Change `DISCOVER_PORT` in .env
- Check: `sudo lsof -i :8080`

**Using Docker Compose V1 instead of V2:**
- Use `docker compose` (with space), not `docker-compose` (with hyphen)
- If you see "ModuleNotFoundError: No module named 'distutils'", upgrade to V2:
  ```bash
  sudo apt remove docker-compose
  sudo apt install docker-compose-plugin
  ```

## Citation
If you use DISCOVER consider citing the following paper:

```
@article{hallmen2025discover,
  title={DISCOVER: a Data-driven Interactive System for Comprehensive Observation, Visualization, and ExploRation of human behavior},
  author={Hallmen, Tobias and Schiller, Dominik and Vehlen, Antonia and Eberhardt, Steffen and Baur, Tobias and Withanage, Daksitha and Lutz, Wolfgang and Andr{\'e}, Elisabeth},
  journal={Frontiers in Digital Health},
  volume={7},
  pages={1638539},
  publisher={Frontiers}
}
```