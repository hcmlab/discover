# Use NVIDIA CUDA base for GPU support (Ubuntu 24.04 has Python 3.12 by default)
FROM nvidia/cuda:12.9.1-runtime-ubuntu24.04

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    curl \
    git \
    ffmpeg \
    build-essential \
    gcc \
    g++ \
    make \
    libssl-dev \
    openssl \
    pkg-config \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3 as default python command
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# Create application user (will be overridden by docker-compose user directive)
RUN groupadd -r discover && useradd -r -g discover discover

# Set working directory
WORKDIR /app

# Create virtual environment for DISCOVER
RUN python3 -m venv /opt/discover-venv

# Upgrade pip in the venv
RUN /opt/discover-venv/bin/pip install --upgrade pip setuptools wheel

# Install DISCOVER from PyPI into the venv
ARG DISCOVER_VERSION=latest
RUN if [ "$DISCOVER_VERSION" = "latest" ]; then \
        /opt/discover-venv/bin/pip install --no-cache-dir hcai-discover; \
    else \
        /opt/discover-venv/bin/pip install --no-cache-dir hcai-discover==$DISCOVER_VERSION; \
    fi

# Make the discover package directory writable for certificate generation
# Use 777 to ensure any user can write (container runs as mapped UID:GID)
RUN chmod -R 777 /opt/discover-venv/lib/python3.12/site-packages/discover

# Add venv to PATH so 'discover' command is available
ENV PATH="/opt/discover-venv/bin:$PATH"

# Copy only the entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod 755 /usr/local/bin/docker-entrypoint.sh

# Create directories for volumes
RUN mkdir -p /app/cache /app/cml /app/data /app/log /app/tmp && \
    chown -R discover:discover /app

# Expose port
EXPOSE 8080

# Health check (dynamically uses http or https based on DISCOVER_USE_TLS)
# Note: Uses shell form (not JSON array) to access environment variables
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD /bin/bash -c 'python -c "import urllib.request, ssl, os; protocol = \"https\" if os.getenv(\"DISCOVER_USE_TLS\", \"false\").lower() == \"true\" else \"http\"; ctx = ssl._create_unverified_context() if protocol == \"https\" else None; urllib.request.urlopen(f\"{protocol}://localhost:8080\", context=ctx).read()"'

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
# CMD uses environment variables from .env file, no hardcoded port needed
CMD ["discover"]
