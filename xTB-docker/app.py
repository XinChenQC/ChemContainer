from fastapi import FastAPI, File, UploadFile, HTTPException
import os
import subprocess
import tempfile
import asyncio
from pathlib import Path

# Environment setup
salad_machine_id = os.getenv("SALAD_MACHINE_ID", "localhost")
app = FastAPI()

# Environment variables are already set in Dockerfile

@app.get("/hello")
async def hello_world():
    return {"message": "Hello, World!", "salad_machine_id": salad_machine_id}

@app.get("/started")
async def startup_probe():
    return {"message": "Started!"}

@app.get("/ready")
async def readiness_probe():
    return {"message": "Ready!"}

@app.get("/live")
async def liveness_probe():
    return {"message": "Live!"}

@app.get("/check")
async def health_check():
    return {"message": "Live!"}
@app.post("/run")
async def run_prediction(yaml_file: UploadFile = File(...)):
    """Run xTB calculation with uploaded YAML configuration"""

    if not yaml_file.filename.endswith(('.yaml', '.yml')):
        raise HTTPException(status_code=400, detail="File must be a YAML file")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        try:
            # Save uploaded file
            yaml_path = temp_path / "config.yaml"
            content = await yaml_file.read()
            with open(yaml_path, "wb") as f:
                f.write(content)

            # Parse YAML
            import yaml
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)

            # Create molecule file
            mol_file = temp_path / "molecule.xyz"
            with open(mol_file, 'w') as f:
                f.write(config.get('coordinates', ''))

            # Build command
            method = config.get('method', 'gfn2')
            charge = config.get('charge', 0)
            multiplicity = config.get('multiplicity', 1)

            cmd = ["xtb", str(mol_file), "--gfn", "2"]

            if charge != 0:
                cmd.extend(["--chrg", str(charge)])
            if multiplicity != 1:
                cmd.extend(["--uhf", str(multiplicity - 1)])

            # Run calculation (environment already set in Dockerfile)
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)

            return {
                "message": "Calculation completed",
                "salad_machine_id": salad_machine_id,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore')
            }

        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Calculation timed out")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")

