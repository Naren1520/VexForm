# VexForm

**From Engineering Drawings to Intelligent 3D Reality.**

VexForm converts 2D mechanical engineering blueprints into validated 3D solid models using:
- **Gemini Vision API** � AI-powered dimension extraction from blueprint images
- **OpenCascade (pythonocc-core)** � True Boolean solid geometry with real material cuts
- **Next.js 15 + React Three Fiber** � Interactive 3D viewer with section view, wireframe, measurement
- **FastAPI** � Backend CAD engine with geometry constraint validation

## Target Part

Lower Valve Body � Injector Assembly (Globe Valve type), Material: HT150

---

## Project Structure

```
vexform/
+-- apps/
�   +-- web/          # Next.js 15 frontend
�   +-- api/          # FastAPI + OpenCascade backend
+-- packages/
    +-- types/        # Shared TypeScript interfaces
```

---

## Quick Start

### Prerequisites

- Node.js 20+
- pnpm 9+
- Python 3.11+
- pythonocc-core 7.9 (see install notes below)

### 1. Clone & install

```bash
git clone <repo>
cd vexform
pnpm install
```

### 2. Environment variables

```bash
cp .env.example .env
# Edit .env and set your GEMINI_API_KEY
```

### 3. Install Python dependencies

```bash
cd apps/api
pip install -r requirements.txt
```

#### Installing pythonocc-core (OpenCascade Python bindings)

pythonocc-core is not on PyPI for all platforms. Use conda:

```bash
conda install -c conda-forge pythonocc-core=7.9.0
```

Or use the pre-built wheel from the pythonocc releases page.

### 4. Run both services

**Terminal 1 � API backend:**
```bash
cd apps/api
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 2 � Frontend:**
```bash
cd apps/web
pnpm dev
```

Open http://localhost:3000

---

## Demo Workflow

1. Open http://localhost:3000 � VexForm landing page
2. Click **Launch CAD Studio**
3. Upload the engineering blueprint (JPEG/PNG/PDF)
4. Click **Analyze Blueprint** � Gemini extracts 28 parameters
5. Review parameters (AI-extracted fields shown in blue, deviations in red)
6. Click **Generate 3D Model** � OpenCascade builds the solid
7. Rotate, zoom the model with mouse
8. Toggle **Wireframe** to see mesh structure
9. Enable **Section** and drag the slider to reveal internal bores
10. Click features in the Feature Tree to highlight geometry
11. Export as **STEP** for manufacturing

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Service health + OCC version |
| `POST` | `/extract` | Upload blueprint ? extract parameters |
| `POST` | `/generate` | Parameters ? 3D solid mesh |
| `GET`  | `/export/step` | Download STEP file |
| `GET`  | `/export/stl` | Download binary STL |
| `GET`  | `/export/obj` | Download Wavefront OBJ |

---

## CAD Pipeline (14 Boolean Operations)

```
1.  Base Cylinder            BRepPrimAPI_MakeCylinder
2.  Top Flange Extrusion     BRepAlgoAPI_Fuse
3.  Bottom Flange Extrusion  BRepAlgoAPI_Fuse
4.  Side Port Boss           BRepAlgoAPI_Fuse (rotated 135�)
5.  Upper Bore Cut           BRepAlgoAPI_Cut  �28mm
6.  Lower Bore Cut           BRepAlgoAPI_Cut  �26mm
7.  Side Port Bore Cut       BRepAlgoAPI_Cut  �20mm @ 135�
8.  Top Bolt Holes Cut       BRepAlgoAPI_Cut  4� �7mm
9.  Top Counterbores Cut     BRepAlgoAPI_Cut  4� �13mm
10. Bottom Bolt Holes Cut    BRepAlgoAPI_Cut  4� �7mm
11. Bottom Counterbores Cut  BRepAlgoAPI_Cut  4� �13mm
12. Side Port Bolt Holes     BRepAlgoAPI_Cut  2� �7mm
13. Fillets                  BRepFilletAPI_MakeFillet  R1mm
14. Chamfers                 BRepFilletAPI_MakeChamfer C1.5mm + C1mm
    ? BRepCheck_Analyzer validation ? mesh tessellation ? Three.js render
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Framer Motion |
| 3D Viewer | Three.js, React Three Fiber, @react-three/drei |
| State | Zustand 5 (5 slices) |
| Backend | Python 3.11, FastAPI 0.115 |
| CAD Kernel | pythonocc-core 7.9 (OpenCascade) |
| AI | Google Gemini 1.5 Flash (Vision) |
| Monorepo | Turborepo + pnpm workspaces |
