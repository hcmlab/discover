# Running Multiple DISCOVER Instances for Multi-GPU Setup

## Overview

You can run multiple DISCOVER containers in parallel to maximize GPU utilization. This supports two strategies:

1. **One container per GPU** - Distribute work across multiple GPUs
2. **Multiple containers per GPU** - Maximize large GPU memory (e.g., 6 containers on H200 with 144GB VRAM)

## Use Cases

- **Multiple concurrent jobs**: Process different sessions/datasets in parallel
- **GPU memory optimization**: Run multiple small jobs on one large GPU (H200, H100, A100)
- **Load balancing**: Distribute work across GPUs and containers
- **GPU isolation**: Assign specific containers to specific GPUs
- **High throughput**: Maximize GPU utilization with many concurrent jobs

## Architecture Examples

### Strategy 1: One Container per GPU (4 GPUs)
```
Host Machine (4 GPUs, e.g., 4x RTX 4090)
├── DISCOVER Instance 1 (GPU 0 exclusive) → Port 8080
├── DISCOVER Instance 2 (GPU 1 exclusive) → Port 8081
├── DISCOVER Instance 3 (GPU 2 exclusive) → Port 8082
└── DISCOVER Instance 4 (GPU 3 exclusive) → Port 8083
```

### Strategy 2: Multiple Containers per GPU (1 Large GPU)
```
Host Machine (1x H200 with 144GB VRAM)
├── DISCOVER Instance 1 (GPU 0 shared, ~24GB) → Port 8080
├── DISCOVER Instance 2 (GPU 0 shared, ~24GB) → Port 8081
├── DISCOVER Instance 3 (GPU 0 shared, ~24GB) → Port 8082
├── DISCOVER Instance 4 (GPU 0 shared, ~24GB) → Port 8083
├── DISCOVER Instance 5 (GPU 0 shared, ~24GB) → Port 8084
└── DISCOVER Instance 6 (GPU 0 shared, ~24GB) → Port 8085
```

### Strategy 3: Hybrid (2 GPUs with multiple containers each)
```
Host Machine (2x H100 with 80GB VRAM each)
├── GPU 0 (80GB)
│   ├── DISCOVER Instance 1 → Port 8080
│   ├── DISCOVER Instance 2 → Port 8081
│   └── DISCOVER Instance 3 → Port 8082
└── GPU 1 (80GB)
    ├── DISCOVER Instance 4 → Port 8083
    ├── DISCOVER Instance 5 → Port 8084
    └── DISCOVER Instance 6 → Port 8085
```

## Method 1: Multiple Compose Files (Recommended)

### A. Multiple Containers on SAME GPU (H200 Example: 6 containers)

For large GPUs like H200 (144GB), H100 (80GB), A100 (80GB), you can run multiple containers sharing the same GPU.

**docker-compose.h200-0.yml:** (Container 1, GPU 0)
```yaml
services:
  discover-h200-0:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        DISCOVER_VERSION: ${DISCOVER_VERSION:-latest}
    container_name: discover-h200-0
    image: discover:latest
    user: "${UID:-1000}:${GID:-1000}"

    ports:
      - "8080:8080"  # Container 1

    volumes:
      - ${HOST_CACHE_DIR:-../cache}:/app/cache
      - ${HOST_CML_DIR:-../cml}:/app/cml:ro
      - ${HOST_DATA_DIR:-../data}:/app/data
      - ${HOST_LOG_DIR:-../log}/h200-0:/app/log
      - ${HOST_TMP_DIR:-../tmp}/h200-0:/app/tmp

    env_file:
      - .env

    environment:
      DISCOVER_HOST: "0.0.0.0"
      DISCOVER_PORT: "8080"
      DISCOVER_CML_DIR: /app/cml
      DISCOVER_DATA_DIR: /app/data
      DISCOVER_CACHE_DIR: /app/cache
      DISCOVER_LOG_DIR: /app/log
      DISCOVER_TMP_DIR: /app/tmp

    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']  # SAME GPU for all containers
              capabilities: [gpu]

    restart: unless-stopped
    healthcheck:
      disable: true
```

**docker-compose.h200-1.yml:** (Container 2, GPU 0)
```yaml
services:
  discover-h200-1:
    # ... same as above except:
    container_name: discover-h200-1
    ports:
      - "8081:8080"  # Different host port
    volumes:
      # ... same volumes but different log/tmp subdirs:
      - ${HOST_LOG_DIR:-../log}/h200-1:/app/log
      - ${HOST_TMP_DIR:-../tmp}/h200-1:/app/tmp
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']  # SAME GPU 0
              capabilities: [gpu]
```

**Repeat for containers 2-5** (ports 8082-8085)

**Key Points for Same-GPU Sharing:**
- ✅ All containers use `device_ids: ['0']` (same GPU)
- ✅ Each container gets different host port (8080, 8081, 8082, ...)
- ✅ Each container gets separate log/tmp directories
- ✅ GPU memory is shared - CUDA manages allocation automatically
- ✅ No explicit memory limits - processes compete for available VRAM
- ⚠️ Monitor with `nvidia-smi` to ensure no OOM errors

**Start all 6 containers on GPU 0:**
```bash
mkdir -p ../log/h200-{0..5} ../tmp/h200-{0..5}

docker compose build

for i in {0..5}; do
  docker compose -f docker-compose.h200-$i.yml up -d
done

# Or all at once
docker compose -f docker-compose.h200-0.yml \
               -f docker-compose.h200-1.yml \
               -f docker-compose.h200-2.yml \
               -f docker-compose.h200-3.yml \
               -f docker-compose.h200-4.yml \
               -f docker-compose.h200-5.yml \
               up -d
```

**Monitor GPU Memory Usage:**
```bash
# Watch all containers sharing GPU 0
watch -n 1 nvidia-smi

# Expected output shows multiple processes on GPU 0:
# +-----------------------------------------------------------------------------+
# | Processes:                                                                  |
# |  GPU   PID   Type   Process name                            GPU Memory     |
# |  0     1234  C      python (discover-h200-0)                3.2GB          |
# |  0     1235  C      python (discover-h200-1)                2.8GB          |
# |  0     1236  C      python (discover-h200-2)                3.5GB          |
# |  0     1237  C      python (discover-h200-3)                2.1GB          |
# |  0     1238  C      python (discover-h200-4)                3.0GB          |
# |  0     1239  C      python (discover-h200-5)                2.9GB          |
# +-----------------------------------------------------------------------------+
```

### B. One Container per GPU (Multi-GPU Setup)

Create separate docker-compose files for each instance:

**docker-compose.gpu0.yml:**
```yaml
services:
  discover-gpu0:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        DISCOVER_VERSION: ${DISCOVER_VERSION:-latest}
    container_name: discover-gpu0
    image: discover:latest
    user: "${UID:-1000}:${GID:-1000}"

    ports:
      - "8080:8080"  # Instance 1 on port 8080

    volumes:
      - ${HOST_CACHE_DIR:-../cache}:/app/cache
      - ${HOST_CML_DIR:-../cml}:/app/cml:ro
      - ${HOST_DATA_DIR:-../data}:/app/data
      - ${HOST_LOG_DIR:-../log}/gpu0:/app/log  # Separate log directory
      - ${HOST_TMP_DIR:-../tmp}/gpu0:/app/tmp  # Separate tmp directory

    env_file:
      - .env

    environment:
      DISCOVER_HOST: "0.0.0.0"
      DISCOVER_PORT: "8080"
      DISCOVER_CML_DIR: /app/cml
      DISCOVER_DATA_DIR: /app/data
      DISCOVER_CACHE_DIR: /app/cache
      DISCOVER_LOG_DIR: /app/log
      DISCOVER_TMP_DIR: /app/tmp

    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']  # GPU 0 only
              capabilities: [gpu]

    restart: unless-stopped
    healthcheck:
      disable: true
```

**docker-compose.gpu1.yml:**
```yaml
services:
  discover-gpu1:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        DISCOVER_VERSION: ${DISCOVER_VERSION:-latest}
    container_name: discover-gpu1
    image: discover:latest
    user: "${UID:-1000}:${GID:-1000}"

    ports:
      - "8081:8080"  # Instance 2 on port 8081

    volumes:
      - ${HOST_CACHE_DIR:-../cache}:/app/cache
      - ${HOST_CML_DIR:-../cml}:/app/cml:ro
      - ${HOST_DATA_DIR:-../data}:/app/data
      - ${HOST_LOG_DIR:-../log}/gpu1:/app/log
      - ${HOST_TMP_DIR:-../tmp}/gpu1:/app/tmp

    env_file:
      - .env

    environment:
      DISCOVER_HOST: "0.0.0.0"
      DISCOVER_PORT: "8080"
      DISCOVER_CML_DIR: /app/cml
      DISCOVER_DATA_DIR: /app/data
      DISCOVER_CACHE_DIR: /app/cache
      DISCOVER_LOG_DIR: /app/log
      DISCOVER_TMP_DIR: /app/tmp

    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['1']  # GPU 1 only
              capabilities: [gpu]

    restart: unless-stopped
    healthcheck:
      disable: true
```

### Create Log/Tmp Directories

```bash
cd /path/to/discover/docker
mkdir -p ../log/gpu{0,1,2,3}
mkdir -p ../tmp/gpu{0,1,2,3}
```

### Start All Instances

```bash
# Build once (image shared by all instances)
docker compose build

# Start each instance
docker compose -f docker-compose.gpu0.yml up -d
docker compose -f docker-compose.gpu1.yml up -d
docker compose -f docker-compose.gpu2.yml up -d
docker compose -f docker-compose.gpu3.yml up -d

# Or start all at once
docker compose -f docker-compose.gpu0.yml \
               -f docker-compose.gpu1.yml \
               -f docker-compose.gpu2.yml \
               -f docker-compose.gpu3.yml \
               up -d
```

### Access Instances

```bash
# Instance 1 (GPU 0)
curl http://localhost:8080

# Instance 2 (GPU 1)
curl http://localhost:8081

# Instance 3 (GPU 2)
curl http://localhost:8082

# Instance 4 (GPU 3)
curl http://localhost:8083
```

### Monitor GPU Usage

```bash
# Check GPU allocation
docker exec discover-gpu0 nvidia-smi
docker exec discover-gpu1 nvidia-smi
docker exec discover-gpu2 nvidia-smi
docker exec discover-gpu3 nvidia-smi

# Or on host
watch -n 1 nvidia-smi
```

### Stop Instances

```bash
# Stop all
docker compose -f docker-compose.gpu0.yml down
docker compose -f docker-compose.gpu1.yml down
docker compose -f docker-compose.gpu2.yml down
docker compose -f docker-compose.gpu3.yml down

# Or
docker compose -f docker-compose.gpu0.yml \
               -f docker-compose.gpu1.yml \
               -f docker-compose.gpu2.yml \
               -f docker-compose.gpu3.yml \
               down
```

## Method 2: Single Compose File with Scale

**docker-compose.multi.yml:**
```yaml
services:
  discover:
    build:
      context: .
      dockerfile: Dockerfile
    image: discover:latest
    user: "${UID:-1000}:${GID:-1000}"

    volumes:
      - ${HOST_CACHE_DIR:-../cache}:/app/cache
      - ${HOST_CML_DIR:-../cml}:/app/cml:ro
      - ${HOST_DATA_DIR:-../data}:/app/data
      - ${HOST_LOG_DIR:-../log}:/app/log
      - ${HOST_TMP_DIR:-../tmp}:/app/tmp

    env_file:
      - .env

    environment:
      DISCOVER_HOST: "0.0.0.0"
      DISCOVER_PORT: "8080"
      DISCOVER_CML_DIR: /app/cml
      DISCOVER_DATA_DIR: /app/data
      DISCOVER_CACHE_DIR: /app/cache
      DISCOVER_LOG_DIR: /app/log
      DISCOVER_TMP_DIR: /app/tmp

    deploy:
      replicas: 4  # Number of instances
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1  # Each instance gets 1 GPU
              capabilities: [gpu]

    restart: unless-stopped
    healthcheck:
      disable: true
```

**Note:** With this method, Docker automatically distributes GPUs, but you have less control over which instance gets which GPU. Ports also need manual configuration.

## Method 3: Docker Swarm (Advanced)

For production clusters with multiple machines:

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.multi.yml discover-stack

# Scale
docker service scale discover-stack_discover=8

# List services
docker service ls

# Remove stack
docker stack rm discover-stack
```

## Resource Sharing Considerations

### Shared Resources
- **Cache directory**: Module venvs are shared (saves disk space)
- **CML directory**: ML modules are shared (read-only)
- **Data directory**: Datasets are shared (ensure no write conflicts)

### Separate Resources
- **Log directory**: Each instance should have its own log directory
- **Tmp directory**: Each instance should have its own tmp directory
- **Ports**: Each instance needs a unique host port

### GPU Memory
- Each GPU has limited memory (8GB, 16GB, 24GB, etc.)
- Monitor with `nvidia-smi`
- Adjust module batch sizes if needed

## Load Balancing

### Manual Distribution
Users submit jobs to specific instances:
```bash
# Send job to GPU 0
curl -X POST http://localhost:8080/api/process ...

# Send job to GPU 1
curl -X POST http://localhost:8081/api/process ...
```

### Nginx Load Balancer (Optional)

**nginx.conf:**
```nginx
upstream discover_backend {
    server localhost:8080;
    server localhost:8081;
    server localhost:8082;
    server localhost:8083;
}

server {
    listen 9000;

    location / {
        proxy_pass http://discover_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Then access via: `http://localhost:9000` (Nginx distributes to all instances)

## GPU Memory Management

### For Multiple Containers on Same GPU

**No Hard Limits by Default:**
- Docker/CUDA does not enforce per-container memory limits
- All containers share GPU VRAM dynamically
- First container to allocate gets the memory
- Containers compete for available memory

**Memory Planning (H200 Example: 144GB VRAM)**
```
6 containers × ~24GB per job = 144GB total
- Container 1: WhisperX large-v3 (~8-10GB)
- Container 2: BlazeFace batch=32 (~4GB)
- Container 3: Emotion recognition (~6GB)
- Container 4: Pose estimation (~8GB)
- Container 5: Object detection (~12GB)
- Container 6: Idle/buffer (~remaining)
```

**Best Practices:**
1. **Monitor actively**: `watch -n 1 nvidia-smi`
2. **Reduce batch sizes**: Set smaller batches in module options
3. **Stagger jobs**: Don't start all 6 containers processing simultaneously at first
4. **Profile first**: Run one container per module type to measure memory usage
5. **Leave headroom**: Don't allocate all 144GB - leave 10-20GB buffer

**If OOM Occurs:**
```bash
# Check which container caused OOM
docker logs discover-h200-3

# Reduce concurrent containers
docker compose -f docker-compose.h200-5.yml down

# Or reduce batch size in module options
# options: {"batch_size": 8}  # Instead of 16
```

### Memory Limits (Advanced - Not Recommended)

NVIDIA doesn't support hard GPU memory limits in Docker, but you can:

**Option 1: CUDA Environment Variables (per container)**
```yaml
environment:
  CUDA_VISIBLE_DEVICES: "0"
  # Limit per-process allocation (not enforced by CUDA)
  PYTORCH_CUDA_ALLOC_CONF: "max_split_size_mb:4096"
```

**Option 2: Module-level batch size control**
```python
# In module options
options = {
    "batch_size": 8,        # Smaller batches = less memory
    "compute_type": "int8", # Lower precision = less memory
}
```

## Performance Tips

1. **Cache Sharing**: All instances share the same cache, so module venvs only need to be created once
2. **Batch Size**: Adjust batch size per container based on available memory
3. **Job Queuing**: Each instance has its own job queue
4. **Monitoring**: Use `nvidia-smi` to watch GPU utilization and memory
5. **Log Rotation**: Each instance creates separate logs, configure rotation
6. **Compute Type**: Use int8/fp16 instead of fp32 to reduce memory usage
7. **Profile First**: Test one container per module type before scaling

## Example 1: H200 with 6 Containers (144GB VRAM)

**Goal**: Maximize single H200 GPU with 6 parallel DISCOVER instances

```bash
# 1. Check GPU
nvidia-smi --query-gpu=name,memory.total --format=csv
# Expected: NVIDIA H200, 147456 MiB (~144GB)

# 2. Create compose files for 6 containers (all using GPU 0)
# Files: docker-compose.h200-{0..5}.yml

# 3. Create directories
mkdir -p ../log/h200-{0..5}
mkdir -p ../tmp/h200-{0..5}

# 4. Build once
docker compose build

# 5. Start all 6 containers
for i in {0..5}; do
  echo "Starting container $i on port 808$i..."
  docker compose -f docker-compose.h200-$i.yml up -d
  sleep 2
done

# 6. Verify all containers see GPU 0
for i in {0..5}; do
  echo "=== Container h200-$i ==="
  docker exec discover-h200-$i nvidia-smi --query-gpu=index,name --format=csv,noheader
done

# Expected: All show "0, NVIDIA H200"

# 7. Monitor memory usage
watch -n 1 nvidia-smi

# 8. Access each instance
curl http://localhost:8080  # Container 0
curl http://localhost:8081  # Container 1
curl http://localhost:8082  # Container 2
curl http://localhost:8083  # Container 3
curl http://localhost:8084  # Container 4
curl http://localhost:8085  # Container 5

# 9. Submit jobs to different containers
curl -X POST http://localhost:8080/api/process -d @job1.json
curl -X POST http://localhost:8081/api/process -d @job2.json
curl -X POST http://localhost:8082/api/process -d @job3.json
# ... etc

# 10. Watch memory distribution
watch -n 2 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv'
```

**Expected Memory Distribution:**
```
GPU 0:
- discover-h200-0: 8-24GB (varies by job)
- discover-h200-1: 8-24GB
- discover-h200-2: 8-24GB
- discover-h200-3: 8-24GB
- discover-h200-4: 8-24GB
- discover-h200-5: 8-24GB
Total: 48-144GB (depending on active jobs)
```

## Example 2: 4 GPUs, 4 Instances

```bash
# 1. Check available GPUs
nvidia-smi --list-gpus

# 2. Create instance configs
# (Use docker-compose.gpu0.yml, gpu1.yml, gpu2.yml, gpu3.yml)

# 3. Build once
docker compose build

# 4. Start all
for i in {0..3}; do
  docker compose -f docker-compose.gpu$i.yml up -d
done

# 5. Verify each instance has correct GPU
for i in {0..3}; do
  echo "Instance GPU$i:"
  docker exec discover-gpu$i nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
done

# 6. Submit jobs to different instances
curl -X POST http://localhost:8080/api/process -d @job1.json  # GPU 0
curl -X POST http://localhost:8081/api/process -d @job2.json  # GPU 1
curl -X POST http://localhost:8082/api/process -d @job3.json  # GPU 2
curl -X POST http://localhost:8083/api/process -d @job4.json  # GPU 3
```

## Troubleshooting

### All Instances Use Same GPU
- Check `device_ids` in docker-compose files
- Ensure NVIDIA Container Toolkit is properly installed
- Verify with: `docker exec <container> nvidia-smi`

### Port Conflicts
- Ensure each instance uses unique host port
- Check with: `sudo lsof -i :8080`

### Shared Cache Conflicts
- Module venv creation is not atomic
- If two instances create same venv simultaneously, one may fail
- Solution: Pre-create venvs by running one job first

### Out of Memory Errors
- Reduce batch sizes in module options
- Monitor with: `watch -n 1 nvidia-smi`
- Consider running fewer instances per GPU

## Cleanup

```bash
# Stop all instances
docker ps --filter "name=discover-gpu" --format "{{.Names}}" | xargs -r docker stop

# Remove all instances
docker ps -a --filter "name=discover-gpu" --format "{{.Names}}" | xargs -r docker rm

# Clean up logs/tmp
rm -rf ../log/gpu*
rm -rf ../tmp/gpu*
```

## Summary

**Best for most users**: Method 1 (separate compose files)
- Full control over GPU assignment
- Easy to start/stop individual instances
- Clear separation of logs and temp files

**Best for clusters**: Method 3 (Docker Swarm)
- Multi-machine support
- Automatic failover
- Built-in orchestration
