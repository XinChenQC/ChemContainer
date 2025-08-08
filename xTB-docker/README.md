# xTB-GFN2 and xTB-g Docker Container

This Docker container provides a FastAPI service for running xTB (extended tight-binding) calculations, including both GFN2 and g-xtb methods.

## Building the Container

1. **Create the project directory and files:**
   ```bash
   mkdir xtb-docker
   cd xtb-docker
   ```

2. **Create all the necessary files** (Dockerfile, app.py, requirements.txt, etc.) from the artifacts above.

3. **Build the Docker image:**
   ```bash
   docker build -t xtb-api .
   ```

4. **Alternative: Use docker-compose:**
   ```bash
   docker-compose up --build
   ```

## Running the Container

### Using Docker directly:
```bash
# Basic run with default OMP settings
docker run -p 8888:8888 --ulimit stack=-1 xtb-api

# Custom OpenMP parameters
docker run -p 8888:8888 --ulimit stack=-1 \
  -e OMP_STACKSIZE=2G \
  -e OMP_NUM_THREADS=2 \
  --memory=4g \
  xtb-api

# Let system auto-decide thread count (recommended)
docker run -p 8888:8888 --ulimit stack=-1 \
  -e OMP_STACKSIZE=1G \
  --memory=4g \
  xtb-api
```

### Using docker-compose:
```bash
docker-compose up
```

### OpenMP Parameter Configuration

- `OMP_STACKSIZE`: Stack size per thread (default: 8G)
- `OMP_NUM_THREADS`: Number of threads to use (default: 1, set to empty for auto)

**Important:** Total stack memory = OMP_STACKSIZE × OMP_NUM_THREADS, ensure it doesn't exceed container memory limit

**Recommended configurations:**
- Small tasks: `OMP_STACKSIZE=1G`, `OMP_NUM_THREADS=1`, `--memory=2g`
- Medium tasks: `OMP_STACKSIZE=2G`, `OMP_NUM_THREADS=2`, `--memory=6g`
- Large tasks: `OMP_STACKSIZE=4G`, `OMP_NUM_THREADS=4`, `--memory=20g`

## API Endpoints

### Health Check Endpoints
- `GET /hello` - Basic hello world with machine ID
- `GET /started` - Startup probe
- `GET /ready` - Readiness probe (checks xTB availability)
- `GET /live` - Liveness probe
- `GET /check` - Health check

### Calculation Endpoints
- `POST /run` - Run xTB calculation with uploaded YAML file
- `GET /info` - Get information about available methods

## Usage Examples

### 1. Check if the service is ready:
```bash
curl http://localhost:8888/ready
```

### 2. Run a calculation:
```bash
# Upload the example YAML file
curl -X POST -F "yaml_file=@example_calculation.yaml" http://localhost:8888/run
```

### 3. Create a simple test file:
```bash
cat > test.yaml << EOF
method: "gfn2"
charge: 0
multiplicity: 1
coordinates: |
  2
  Water molecule
  O 0.0 0.0 0.0
  H 1.0 0.0 0.0
options:
  opt: true
EOF

curl -X POST -F "yaml_file=@test.yaml" http://localhost:8888/run
```

### 4. Remote API call example:
```bash
# Call remote xTB service
curl -X POST -F "yaml_file=@test.yaml" http://your-server.com:8888/run

# Example with real server
curl -X POST -F "yaml_file=@example_calculation.yaml" http://IP:8888/run
```

### 5. Python client example:
```python
import requests

# Remote xTB calculation
def run_xtb_calculation(yaml_file_path, server_url="http://43.153.50.138:8888"):
    with open(yaml_file_path, 'rb') as f:
        files = {'yaml_file': f}
        response = requests.post(f"{server_url}/run", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Calculation completed: {result['message']}")
        print(f"Return code: {result['return_code']}")
        if result['return_code'] == 0:
            print("Success!")
        else:
            print(f"Error: {result['stderr']}")
        return result
    else:
        print(f"API Error: {response.status_code}")
        print(response.text)
        return None

# Usage
result = run_xtb_calculation("example_calculation.yaml")
```

### 6. Get service information:
```bash
# Local service
curl http://localhost:8888/info

# Remote service
curl http://IP:8888/info
```

## YAML Configuration Format

The calculation YAML file should contain:

```yaml
method: "gfn2"  # Options: gfn2
charge: 0
multiplicity: 1
coordinates: |
  # XYZ format coordinates
  number_of_atoms
  comment_line
  element x y z
  element x y z
  ...
options:
  opt: true        # Geometry optimization
  freq: true       # Frequency calculation
  solvent: "water" # Implicit solvation
```

## Environment Variables

- `SALAD_MACHINE_ID`: Machine identifier (defaults to "localhost")
- `OMP_STACKSIZE`: OpenMP stack size per thread (defaults to 8G)
- `OMP_NUM_THREADS`: Number of OpenMP threads (defaults to 1, set to empty for auto)
- `XTB_HOME`: xTB installation directory (/opt/xtb)

**Note:** Total stack memory usage = OMP_STACKSIZE × OMP_NUM_THREADS

## Features

- **xTB-GFN2**: Fast semi-empirical quantum chemical calculations
- **Stack size management**: Automatically sets unlimited stack size
- **OpenMP configuration**: Optimized for parallel calculations
- **File upload support**: Accept YAML configuration files
- **Health monitoring**: Multiple health check endpoints
- **Error handling**: Comprehensive error reporting and timeouts

## Troubleshooting

1. **Stack size issues**: The container automatically sets unlimited stack size, but if you encounter stack overflow errors, ensure the `--ulimit stack=-1` flag is used when running Docker.

2. **Memory issues**: Large calculations may require more memory. Adjust the memory limits in docker-compose.yml or use `--memory` flag with docker run.

3. **OpenMP resource errors**: If you see "System unable to allocate necessary resources for OMP thread", reduce `OMP_NUM_THREADS` or increase container memory allocation.

4. **Timeout issues**: Large calculations have a 5-minute timeout. This can be adjusted in the code if needed.

5. **Permission issues**: If you encounter permission issues, you may need to run the container with appropriate user permissions.

## Development Notes

- The container installs xTB v6.7.1 from the official release
- The FastAPI application includes comprehensive error handling and logging
- All calculations run in temporary directories for isolation
- Output files are captured and returned in the API response
- Environment variables can be overridden at container runtime for flexible configuration
