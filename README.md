# ChemContainer (Developing)
To standardize the computational chemistry calculation input or output in containers.

## Structure and abstract concept

* **Case**:
  Provides overall interface APIs to users
* **Motherboard**:
  Drivers that provide high-level integration, like MD, geometry optimization, ...
* **Engines**:
  Basic computational programs
* **Bus**:
  Communication between Engines

## Folder

### DockerFiles

    * Different Cloud Provider (Salad, Nebius, AWS)
    * GPU/CPU

### Fastapi_general 

### App

   * Interact with FastAPI.
   * Different functions
   * Single funcion
     1. MSA (multi sequence alignment)
     2. Diffdock (Molecular docking)
    
### Document

  * Readmydoc

