<div align="center">

# VexForm

### From Engineering Drawings to Intelligent 3D Reality

VexForm converts 2D mechanical engineering blueprints into validated, interactive 3D solid models -powered by AI vision and a real CAD kernel.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js&logoColor=white)](https://nextjs.org)
[![OpenCascade](https://img.shields.io/badge/OpenCascade-7.9-blue)](https://dev.opencascade.org)
[![Gemini](https://img.shields.io/badge/Gemini-3.6_Flash-8B5CF6?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Project Workflow](#project-workflow)
- [CAD Pipeline](#cad-pipeline-14-boolean-operations)
- [Folder Structure](#folder-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Project](#running-the-project)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [State Management](#state-management)
- [Developer](#developer)

---

## Overview

VexForm is a full-stack intelligent CAD platform targeting mechanical engineers. Upload a blueprint image (JPEG / PNG / PDF), and the system:

1. Sends the drawing to **Gemini 3.6 Flash** for multi-view engineering interpretation.
2. Parses the response into a strict, structured **CAD-IR feature graph** with dimensions, dependencies, confidence, and evidence.
3. Validates the graph, resolves topology references, and executes trusted features through **FastAPI + OpenCascade 7.9**.
4. Streams the validated B-Rep tessellation to the interactive Three.js viewer with review, section, measurement, feature-tree, and STEP / STL / OBJ export support.

**Target part:** Lower Valve Body -Injector Assembly (Globe Valve type), Material: HT150

### Generic CAD-IR architecture

The generic path is now based on **CAD-IR**, a validated Pydantic feature graph. Gemini interprets views, dimensions, and engineering features into structured JSON; it never produces executable Python. A trusted feature registry executes the validated graph through OpenCascade, then produces the authoritative B-Rep for mesh and STEP/STL/OBJ export. The legacy Lower Valve Body parameter path remains available for regression compatibility while parts are migrated.

CAD-IR supports extensible primitive, Boolean, hole/pattern, transform, and finishing features. An optional `EngineeringKnowledgeProvider` interface is available for future drawing-standard and GD&T retrieval.

Increment 3 executes sketches (line, polyline, circle, arc, and ellipse), extrude, revolve, sweep, loft, rib, primitives, Booleans, holes, patterns, fillets, chamfers, shell, and draft through trusted OCC handlers. Stable feature-relative topology metadata is used for face and edge references; ambiguous or missing references return structured errors.

The end-to-end reconstruction path accepts multiple drawing views in one CAD-IR document, retains confidence and evidence fields for uncertain dimensions/features, validates cross-feature constraints before OCC, and records feature-level timing and topology lineage where available. All blueprint uploads now use this generic CAD-IR path; the older named-shape builders remain only as compatibility code for legacy API clients. It is designed for progressively broader mechanical drawing support, not universal blueprint reconstruction.

### Blueprint Understanding Pipeline

Local or uploaded drawings can be interpreted through a provider boundary: `RealGeminiProvider` uses Gemini Vision and `MockGeminiProvider` reads deterministic local fixtures for offline development and CI. Both produce the same strict `CADModel` contract. The review flow is `EXTRACTING -> EXTRACTED -> NEEDS_REVIEW -> VALIDATED -> GENERATING -> GENERATED`; low confidence and semantic conflicts remain reviewable instead of being silently repaired.

Models can be persisted behind the filesystem-backed `ModelStore`, which stores the blueprint metadata, CAD-IR, validation state, metrics, and immutable revision records. Each modification or rollback creates a new revision while CAD-IR remains the source of truth. A measured benchmark helper records validation, OCC success, feature counts, confidence, B-Rep metrics, and elapsed time for fixture comparisons.

### Topology Reference System

Each generated OCC feature receives topology metadata for its faces, edges, and vertices. References are feature-relative and paired with geometric signatures such as surface or curve type, area or length, centroid, radius, normal, and axis. Downstream operations resolve these signatures with tolerances; raw OCC enumeration indices are never public identifiers. Boolean and finishing results receive newly extracted metadata, and ambiguous or missing matches return structured CAD errors instead of selecting arbitrary geometry.

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend framework | Next.js | 16.3.1 |
| UI language | TypeScript | 5.7.2 |
| Styling | Tailwind CSS | 3.4.17 |
| Animation | Framer Motion | 11.15.0 |
| 3D rendering | Three.js + React Three Fiber | 0.169 / 9.7.0 |
| 3D helpers | @react-three/drei | 10.7.8 |
| State management | Zustand | 5.0.3 |
| Backend framework | FastAPI | 0.115.6 |
| Backend runtime | Python | 3.11+ |
| CAD kernel | pythonocc-core (OpenCascade) | 7.9.0 |
| AI / Vision | Google Gemini 3.6 Flash | Configurable with `GEMINI_MODEL` |
| Validation | Pydantic | 2.9.2 |
| Monorepo tooling | Turborepo + pnpm workspaces | -|
| Frontend tests | Vitest + Testing Library | 2.1.8 |
| Backend tests | pytest + pytest-asyncio | 8.3.4 |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                              │
│                                                             │
│   ┌────────────┐   ┌──────────────────┐     ┌─────────────┐ │
│   │  Landing   │   │   CAD Studio     │     │  Inspector  │ │
│   │  Page      │──▶│  (Next.js 16)    │◀─▶│  Panel      │ │
│   └────────────┘   │                  │     └─────────────┘ │
│                    │  • Upload Zone   │                     │
│                    │  • Param Review  │                     │
│                    │  • 3D Viewport   │                     │
│                    │  • Feature Tree  │                     │
│                    └────────┬─────────┘                     │
└─────────────────────────────│───────────────────────────────┘
                              │ HTTP / JSON
                    ┌─────────▼─────────┐
                    │   FastAPI Server  │
                    │   (Python 3.11)   │
                    │                   │
                    │  ┌─────────────┐  │
                    │  │ /extract    │──┼──▶ Gemini 3.6 Flash
                    │  │ /generate   │  │    Vision API
                    │  │ /export/*   │  │
                    │  │ /health     │  │
                    │  └──────┬──────┘  │
                    │         │         │
                    │  ┌──────▼──────┐  │
                    │  │ CAD-IR/OCC  │  │
                    │  │ trusted     │  │
                    │  │ feature graph│  │
                    │  └─────────────┘  │
                    └───────────────────┘
```

---

## Project Workflow

```
 ┌──────────────────────────────────────────────────────────────────┐
 │  1. USER uploads blueprint image (JPEG / PNG / PDF, max 20 MB)   │
 └───────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  2. POST /extract                                                │
 │     • Image sent to Gemini 3.6 Flash Vision API                  │
 │     • All drawing views are unified into one CAD-IR graph         │
 │     • Dimensions include confidence, source, and uncertainty      │
 │     • Returns: CAD-IR + review state + validation context        │
 └───────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  3. HUMAN REVIEW -user checks the interpretation                 │
 │     • Low-confidence features and dimensions require review       │
 │     • Evidence and topology metadata remain available             │
 │     • User can edit or disable features before generation         │
 └───────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  4. POST /validate then /generate                                 │
 │     • CAD-IR schema and semantic constraints are checked          │
 │     • Dependency graph resolves in trusted OCC executor           │
 │     • BRepCheck validates the resulting solid                    │
 │     • Returns: mesh + dynamic feature tree + metrics              │
 └───────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  5. 3D VIEWPORT -interactive model in React Three Fiber         │
 │     • Orbit / pan / zoom with mouse                              │
 │     • Wireframe toggle (see mesh tessellation)                   │
 │     • Section view: drag clip plane to reveal internal bores     │
 │     • Measurement tool: click two points → live distance readout │
 │     • Scale bar adapts to zoom level                             │
 │     • Feature tree: click node to highlight geometry region      │
 └───────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  6. EXPORT -one-click download                                  │
 │     • STEP  -full parametric solid for CNC / CAM software       │
 │     • STL   -binary mesh for 3D printing / FEA                  │
 │     • OBJ   -Wavefront format for rendering / game engines      │
 └──────────────────────────────────────────────────────────────────┘
```

---

## Generic CAD Pipeline

```
Blueprint → Gemini 3.6 Flash → CAD-IR → Pydantic validation
     → semantic review → dependency graph → trusted feature registry
     → OpenCascade 7.9 → topology lineage → BRepCheck
     → tessellation → Three.js / STEP / STL / OBJ

Supported generic features include primitives, sketches, extrude, revolve, sweep,
loft, Booleans, holes, patterns, fillets, chamfers, shell, draft, rib, and transforms.
The original valve implementation remains only as a legacy compatibility path and is
not selected by the normal blueprint upload flow.
```

---

## Folder Structure

```
VexForm/
├── apps/
│   ├── api/                          # FastAPI backend -CAD geometry engine
│   │   ├── main.py                   # App factory, CORS middleware, routers
│   │   ├── requirements.txt          # pip dependencies
│   │   ├── pyproject.toml            # Project metadata + pytest config
│   │   ├── .env                      # Local env vars (gitignored)
│   │   └── app/
│   │       ├── config.py             # Pydantic settings (reads .env)
│   │       ├── models/
│   │       │   ├── params.py         # LowerValveBodyParams (28 fields, Pydantic)
│   │       │   ├── generate_response.py  # GenerateResponse, FeatureNode
│   │       │   ├── mesh_payload.py   # MeshPayload, BoundingBox
│   │       │   └── errors.py         # ValidationError model
│   │       ├── routers/
│   │       │   ├── health.py         # GET /health
│   │       │   ├── extract.py        # POST /extract -Gemini Vision
│   │       │   ├── generate.py       # POST /generate -OCC pipeline
│   │       │   └── export.py         # GET /export/{step,stl,obj}
│   │       ├── services/
│   │       │   ├── gemini_client.py  # Compatibility extraction client
│   │       │   ├── blueprint_to_program.py # Gemini 3.6 Flash → CAD-IR
│   │       │   ├── extraction_provider.py # Real/mock provider boundary
│   │       │   ├── confidence.py       # Deterministic confidence scoring
│   │       │   ├── model_store.py       # Filesystem model revisions
│   │       │   ├── geometry_engine.py # 14-step OCC Boolean pipeline
│   │       │   ├── mesh_serialiser.py # OCC shape → float32 vertex/index/normal
│   │       │   ├── validator.py      # Geometry constraint checks
│   │       │   └── fallback_mesh.py  # Reference mesh when OCC unavailable
│   │       └── reference/
│   │           └── lower_valve_body.py  # Hardcoded reference dimensions
│   │
│   └── web/                          # Next.js 16 frontend
│       ├── next.config.ts
│       ├── package.json
│       ├── postcss.config.js
│       ├── tailwind.config  (via postcss)
│       └── src/
│           ├── app/
│           │   ├── layout.tsx        # Root layout, fonts
│           │   ├── page.tsx          # Landing page (/, marketing)
│           │   ├── globals.css       # Tailwind base + custom tokens
│           │   ├── not-found.tsx     # 404 page
│           │   └── studio/
│           │       ├── layout.tsx    # Studio shell layout
│           │       └── page.tsx      # CAD Studio -3-panel layout
│           ├── components/
│           │   ├── landing/          # Marketing landing page sections
│           │   │   ├── LandingNav.tsx
│           │   │   ├── HeroSection.tsx
│           │   │   ├── HowItWorks.tsx
│           │   │   ├── FeaturesGrid.tsx
│           │   │   ├── TechnicalShowcase.tsx
│           │   │   └── CTASection.tsx
│           │   ├── studio/           # Studio shell components
│           │   │   ├── Toolbar.tsx
│           │   │   ├── InspectorPanel.tsx
│           │   │   ├── PanelDivider.tsx  # Resizable panel drag handle
│           │   │   └── ToastContainer.tsx
│           │   ├── upload/           # Blueprint upload flow
│           │   │   ├── FileUploadZone.tsx
│           │   │   └── BlueprintPreview.tsx
│           │   ├── params/           # Parameter review form
│           │   │   ├── ParamReviewForm.tsx
│           │   │   ├── ParamField.tsx
│           │   │   └── ParamStatusIcon.tsx
│           │   ├── viewport/         # 3D viewer (React Three Fiber)
│           │   │   ├── Viewport.tsx       # Canvas, camera, lighting
│           │   │   ├── ModelMesh.tsx      # BufferGeometry from MeshPayload
│           │   │   ├── SectionViewPlane.tsx  # Clipping plane slider
│           │   │   ├── MeasurementTool.tsx   # Click-to-measure
│           │   │   └── ScaleBar.tsx          # Dynamic scale indicator
│           │   └── feature-tree/     # CAD feature tree
│           │       ├── FeatureTree.tsx
│           │       └── FeatureTreeNode.tsx
│           ├── store/                # Zustand global state (5 slices)
│           │   ├── index.ts          # Store composition + devtools
│           │   └── slices/
│           │       ├── uploadSlice.ts
│           │       ├── extractionSlice.ts
│           │       ├── geometrySlice.ts
│           │       ├── viewportSlice.ts
│           │       └── uiSlice.ts
│           └── lib/
│               └── bufferGeometry.ts # MeshPayload → Three.js BufferGeometry
│
├── packages/
│   └── types/                        # Shared TypeScript interfaces
│       └── index.ts                  # MeshPayload, FeatureNode, LowerValveBodyParams
│
├── .env                              # Root env (gitignored)
├── .env.example                      # Env template (commit this)
├── .gitignore
├── package.json                      # Root pnpm workspace config
├── pnpm-workspace.yaml               # Workspace declarations
└── turbo.json                        # Turborepo pipeline config
```

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Node.js | 20+ | [nodejs.org](https://nodejs.org) |
| pnpm | 9+ | `npm install -g pnpm` |
| Python | 3.11+ | [python.org](https://python.org) |
| Conda | latest | Required for `pythonocc-core` -[Miniconda](https://docs.conda.io/en/latest/miniconda.html) |
| Git | any | -|

You also need a **Google Gemini API key** (free tier works):
[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/narensj20/vexform.git
cd VexForm
```

### 2. Install frontend dependencies

```bash
pnpm install
```

### 3. Set up environment variables

```bash
# Windows CMD
copy .env.example .env

# Windows PowerShell / Git Bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash
SESSION_SECRET=any-random-string
API_BASE_URL=http://localhost:8001
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
```

Also copy the API-level env:

```bash
# CMD
copy .env.example apps\api\.env

# PowerShell
cp .env.example apps/api/.env
```

### 4. Set up the Python environment (Conda -recommended)

`pythonocc-core` (OpenCascade Python bindings) is only reliably available via conda-forge.

#### Option A -Create a fresh conda environment (recommended)

```bash
# Open Anaconda Prompt / Miniconda Prompt and run:

conda create -n vexform python=3.11 -y
conda activate vexform

conda install -c conda-forge pythonocc-core=7.9.0 -y

cd apps/api
pip install -r requirements.txt
```

#### Option B -Add to an existing conda environment

```bash
conda activate <your-env>
conda install -c conda-forge pythonocc-core=7.9.0 -y

cd apps/api
pip install -r requirements.txt
```

#### Option C -pip only (no OCC, fallback mesh mode)

If you skip the conda step, the API will start in **fallback mesh mode** -it uses hardcoded reference geometry instead of live OpenCascade computation. All other features (Gemini extraction, parameter review, 3D viewer, export) remain fully functional.

```bash
cd apps/api
pip install -r requirements.txt
```

---

## Running the Project

You need **two terminals** running simultaneously.

### Terminal 1 -API Backend

```bash
# Activate your conda environment first
conda activate vexform

# Navigate to the API folder
cd apps/api

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Interactive API docs available at: **http://localhost:8001/docs**

---

### Terminal 2 -Frontend (Next.js)

```bash
# From the project root
cd apps/web
pnpm dev
```

Expected output:
```
  ▲ Next.js 16.3.1
  - Local:        http://localhost:3000
  - Network:      http://0.0.0.0:3000
  ✓ Ready in 2.1s
```

Open: **http://localhost:3000**

---

### Full Conda Prompt Workflow (copy-paste ready)

```bash
#  One-time setup 
conda create -n vexform python=3.11 -y
conda activate vexform
conda install -c conda-forge pythonocc-core=7.9.0 -y
pip install -r apps/api/requirements.txt
pnpm install

#  Daily start: Terminal 1 (API) 
conda activate vexform
uvicorn main:app --reload --host 0.0.0.0 --port 8001

#  Daily start: Terminal 2 (Web) -open a new terminal 
cd apps/web
pnpm devcd apps/api

```

---

### Using Turborepo (runs both services together)

```bash
# From project root
pnpm turbo dev
```

> Note: Turborepo runs Node-based tasks natively but will not auto-activate your conda environment for the Python server. If you use this shortcut, make sure your conda environment is already active in your shell.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google Gemini Vision API key |
| `GEMINI_MODEL` | No | Gemini model used for structured CAD-IR extraction (default: `gemini-3.6-flash`) |
| `SESSION_SECRET` | No | Session signing secret (default: dev value) |
| `API_BASE_URL` | No | Internal server-side API URL (default: `http://localhost:8000`) |
| `NEXT_PUBLIC_API_BASE_URL` | Yes | Public client-side API URL -must match where uvicorn is running |

The API server reads its key from `apps/api/.env` or the root `.env` (both are checked automatically via Pydantic Settings).

---

## API Reference

Base URL: `http://localhost:8001`

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Service health check + OpenCascade version |
| `POST` | `/extract` | Upload blueprint image → Gemini 3.6 Flash → CAD-IR + review context |
| `POST` | `/generate` | Submit CAD-IR → build validated B-Rep → return mesh + feature tree |
| `POST` | `/validate` | Validate a CAD-IR document without executing geometry |
| `POST` | `/modify` | Apply a structured update/add/remove to CAD-IR and rebuild |
| `GET` | `/export/step` | Download generated model as STEP (requires OCC) |
| `GET` | `/export/stl` | Download generated model as binary STL (requires OCC) |
| `GET` | `/export/obj` | Download generated model as Wavefront OBJ (requires OCC) |
| `GET` | `/debug/occ` | Check if OpenCascade is available in main + worker threads |
| `GET` | `/debug/occ-full` | Run a minimal Boolean cut test end-to-end |

### POST /extract

- **Content-Type:** `multipart/form-data`
- **Field:** `blueprint` -image file (JPEG / PNG / PDF, max 20 MB)
- **Response:**
```json
{
  "shape_type": "programmatic",
  "cad_ir": {
    "version": "1.0",
    "units": "mm",
    "views": [{ "id": "front", "view_type": "front", "features": ["base"] }],
    "features": [{
      "id": "base",
      "type": "extrude",
      "depends_on": ["base_sketch"],
      "confidence": 0.92,
      "evidence": [{ "source": "front_view", "reason": "explicit dimension" }]
    }]
  },
  "review_state": "NEEDS_REVIEW",
  "source": "gemini",
  "elapsed_ms": 1243.5
}
```

### POST /generate

- **Content-Type:** `application/json`
- **Header:** `X-Session-Token: <uuid>` (used to correlate with export calls)
- **Body:** `{ "shape_type": "programmatic", "params": { "cad_ir": { ... } } }`
- **Response:**
```json
{
  "mesh": {
    "vertices": [...],
    "indices": [...],
    "normals": [...],
    "bounding_box": { "min": [x, y, z], "max": [x, y, z] }
  },
  "feature_tree": [
    { "id": "base", "label": "Base Feature", "status": "success", "confidence": 0.92 }
  ],
  "elapsed_ms": 4821.0
}
```

---

## State Management

The frontend uses **Zustand 5** with a single composed store of 5 slices:

| Slice | Responsibility |
|---|---|
| `uploadSlice` | Blueprint file, upload status, preview URL |
| `extractionSlice` | API call to `/extract`, extracted params, source flag |
| `geometrySlice` | API call to `/generate`, mesh payload, feature tree, selection |
| `viewportSlice` | Wireframe toggle, section plane position, measurement state, panel widths |
| `uiSlice` | Toast notifications, loading overlays |

The store is connected to **Redux DevTools** under the name `VexFormStore` for easy debugging.

---

## Developer

<table>
<tr>
<td align="center">
<b>Naren S J</b><br/>
 Software Engineer · AI/ML Engineer · Problem Solver<br/><br/>
<a href="mailto:narensonu1520@gmail.com">narensonu1520@gmail.com</a><br/>
<a href="tel:+918296833381">+91 82968 33381</a><br/>
<a href="https://narensj.netlify.app">narensj.netlify.app</a><br/>
<a href="https://www.linkedin.com/in/narensj20">linkedin.com/in/narensj20</a><br/>
<a href="https://github.com/narensj20">github.com/narensj20</a>
</td>
</tr>
</table>

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'OCC'`**
→ `pythonocc-core` is not installed or you are running from the wrong Python environment. Run `conda activate vexform` before starting uvicorn.

**`NEXT_PUBLIC_API_BASE_URL` mismatch**
→ If uvicorn is on port 8001, set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8001` in both root `.env` and `apps/web/.env.local`.

**Gemini returns `source: "fallback"`**
→ Check your `GEMINI_API_KEY` is valid and not rate-limited. The API will silently use reference dimensions as a fallback so the rest of the pipeline still works.

**Generation times out (>120s)**
→ Complex OCC Boolean operations can be slow on first run. Subsequent calls are faster. If it consistently fails, check the `/debug/occ-full` endpoint to confirm OCC is working.

**`conda install pythonocc-core` hangs**
→ Try adding `--no-deps` and installing dependencies separately, or use `mamba` as a faster conda solver: `conda install -c conda-forge mamba -y && mamba install -c conda-forge pythonocc-core=7.9.0`.

---

<div align="center">

Built with precision by **Naren S J** · [narensj.netlify.app](https://narensj.netlify.app)

</div>

conda activate vexform
cd /d "C:\Users\Naren S J\Downloads\VexForm\apps\api"
set PYTHONPATH=C:\Users\Naren S J\Downloads\VexForm\apps\api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001