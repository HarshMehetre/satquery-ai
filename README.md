# SatQuery-AI

> **An AI-powered geospatial analyst that converts natural-language questions into executable satellite-image and GIS operations, producing evidence-backed spatial answers.**

---

## Overview

**SatQuery-AI** is a natural-language interface for satellite imagery and geospatial analysis.

Instead of requiring a user to manually search satellite datasets, process raster imagery, calculate spectral indices, perform GIS operations, and interpret the results, SatQuery allows the user to ask questions in natural language.

For example:

> **"Find areas where vegetation decreased between 2024 and 2026 that are within 3 km of major roads."**

SatQuery interprets the question, determines the required datasets and operations, executes the analysis, and returns the result as a spatial visualization with supporting evidence.

The core idea is:

```text
Natural Language
       ↓
Query Understanding
       ↓
Execution Plan
       ↓
Satellite + Geospatial Data
       ↓
Remote Sensing + GIS Operations
       ↓
Spatial / Temporal Reasoning
       ↓
Evidence
       ↓
Map + Natural Language Answer
```

SatQuery is therefore not intended to be simply a **chatbot for satellite images**.

It is designed as a **natural-language geospatial reasoning and execution system**.

---

# 1. Problem

Working with satellite imagery currently requires knowledge of several independent technologies:

* Satellite data catalogues
* Remote sensing
* Raster processing
* Spectral indices
* Computer vision
* GIS
* Spatial databases
* Coordinate systems
* Temporal analysis
* Geospatial visualization

A user may know **what they want to know** without knowing **how to perform the analysis**.

For example:

> "Which agricultural areas experienced vegetation loss and are close to major roads?"

Answering this manually requires:

1. Obtaining satellite imagery.
2. Selecting suitable imagery from different dates.
3. Computing vegetation information.
4. Identifying agricultural regions.
5. Obtaining road data.
6. Filtering major roads.
7. Creating a distance buffer.
8. Intersecting the datasets.
9. Calculating affected area.
10. Visualizing the result.
11. Explaining the evidence.

SatQuery aims to automate this entire chain.

---

# 2. Core Concept

The fundamental design principle of SatQuery is:

> **LLM plans. Code executes.**

The language model should understand the user's intent and generate a structured execution plan.

It should **not** directly perform geospatial calculations or invent results.

For example:

```text
User:
"Find vegetation loss within 3 km of major roads."

                ↓

LLM / Query Planner

                ↓

Structured QueryPlan

                ↓

Deterministic Executor

                ↓

Satellite Retrieval
NDVI Calculation
Temporal Comparison
Road Retrieval
Road Filtering
3 km Buffer
Intersection
Area Calculation

                ↓

Evidence-backed Result
```

This separation provides:

* Deterministic execution
* Reproducibility
* Validation
* Easier debugging
* Better security
* Extensibility
* Reduced hallucination risk

---

# 3. System Architecture

The high-level architecture is:

```text
┌──────────────────────────────────────────────┐
│                 USER                         │
│                                              │
│ "Find vegetation loss near major roads"      │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│            QUERY UNDERSTANDING               │
│                                              │
│ • Intent extraction                          │
│ • Entity identification                      │
│ • Spatial constraints                        │
│ • Temporal constraints                       │
│ • Required analysis                          │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              QUERY PLANNER                   │
│                                              │
│ Converts natural language into a validated   │
│ structured QueryPlan                         │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│             EXECUTION ENGINE                │
│                                              │
│ • Dependency resolution                      │
│ • Operation validation                       │
│ • Operation execution                        │
│ • Result management                          │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
┌────────────┐  ┌─────────────┐  ┌─────────────┐
│ Satellite  │  │ Remote      │  │ GIS         │
│ Data       │  │ Sensing     │  │ Operations  │
│            │  │             │  │             │
│ Sentinel-2 │  │ NDVI        │  │ Buffer      │
│ Sentinel-1 │  │ NDWI        │  │ Intersection│
│            │  │ Change      │  │ Distance    │
│            │  │ Detection   │  │ Area        │
└─────┬──────┘  └──────┬──────┘  └──────┬──────┘
      │                │                │
      └────────────────┼────────────────┘
                       ▼
┌──────────────────────────────────────────────┐
│          SPATIAL / TEMPORAL REASONING        │
│                                              │
│ • Filtering                                  │
│ • Ranking                                    │
│ • Temporal comparison                        │
│ • Multi-layer spatial reasoning              │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              EVIDENCE LAYER                  │
│                                              │
│ • Source imagery                             │
│ • Acquisition date                           │
│ • Operations performed                       │
│ • Parameters                                 │
│ • Confidence / quality information           │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                 OUTPUT                       │
│                                              │
│ • Interactive map                            │
│ • Spatial overlays                           │
│ • Statistics                                 │
│ • Natural-language explanation               │
│ • Evidence                                   │
└──────────────────────────────────────────────┘
```

---

# 4. System Workflow

Every SatQuery request follows a structured pipeline.

## Step 1 — Natural Language Query

The user asks a geospatial question.

Example:

```text
Find areas where vegetation decreased between
2024 and 2026 that are within 3 km of major roads.
```

---

## Step 2 — Query Understanding

The system identifies:

* Area of interest
* Objects/features
* Temporal range
* Spatial constraints
* Required measurements
* Required datasets
* Required analytical operations

The query is transformed from natural language into machine-understandable intent.

---

## Step 3 — Query Planning

The planner converts the intent into a structured `QueryPlan`.

For the example above, the planner determines that the system needs:

```text
Sentinel-2 imagery
        +
2024 vegetation analysis
        +
2026 vegetation analysis
        +
Temporal vegetation comparison
        +
Major road data
        +
3 km road buffer
        +
Spatial intersection
        +
Area calculation
```

The planner does not execute these operations.

It only specifies **what needs to happen**.

---

# 5. QueryPlan

The QueryPlan is the contract between the planner and the execution engine.

Conceptually:

```text
QueryPlan
│
├── plan_id
│
├── aoi
│
├── inputs
│
├── operations
│
└── output
```

Example:

```json
{
  "plan_id": "hero_001",

  "aoi": {
    "type": "polygon",
    "value": "USER_AOI"
  },

  "inputs": [
    {
      "id": "s2_2024",
      "source": "sentinel-2",
      "purpose": "vegetation",
      "time_range": {
        "start": "2024-01-01",
        "end": "2024-12-31"
      }
    },
    {
      "id": "s2_2026",
      "source": "sentinel-2",
      "purpose": "vegetation",
      "time_range": {
        "start": "2026-01-01",
        "end": "2026-12-31"
      }
    },
    {
      "id": "roads",
      "source": "osm",
      "purpose": "major_roads"
    }
  ],

  "operations": [
    {
      "id": "ndvi_2024",
      "type": "calculate_ndvi",
      "inputs": ["s2_2024"]
    },
    {
      "id": "ndvi_2026",
      "type": "calculate_ndvi",
      "inputs": ["s2_2026"]
    },
    {
      "id": "vegetation_change",
      "type": "temporal_difference",
      "inputs": ["ndvi_2024", "ndvi_2026"]
    },
    {
      "id": "vegetation_loss",
      "type": "filter",
      "inputs": ["vegetation_change"],
      "parameters": {
        "condition": "decrease"
      }
    },
    {
      "id": "major_roads",
      "type": "filter",
      "inputs": ["roads"],
      "parameters": {
        "class": "major"
      }
    },
    {
      "id": "road_buffer",
      "type": "buffer",
      "inputs": ["major_roads"],
      "parameters": {
        "distance_m": 3000
      }
    },
    {
      "id": "final",
      "type": "intersection",
      "inputs": [
        "vegetation_loss",
        "road_buffer"
      ]
    },
    {
      "id": "area",
      "type": "calculate_area",
      "inputs": ["final"]
    }
  ],

  "output": {
    "type": "map",
    "include_geometry": true,
    "include_statistics": true,
    "include_evidence": true
  }
}
```

---

# 6. Operation-Based Execution

SatQuery uses small, composable operations instead of large monolithic functions.

Each operation performs **one semantic action**.

For example:

```text
calculate_ndvi
```

is preferable to:

```text
download_satellite_calculate_ndvi_detect_change_and_filter_roads
```

This makes the system modular and allows new capabilities to be added without changing the entire architecture.

---

# 7. Operation Primitive Library

The initial operation library is planned around four categories.

## Data Operations

```text
get_satellite_imagery()
get_osm_features()
```

---

## Remote Sensing Operations

```text
calculate_ndvi()
calculate_ndwi()
classify_landcover()
detect_change()
segment_water()
```

---

## GIS Operations

```text
buffer()
intersect()
clip()
within_distance()
calculate_area()
calculate_statistics()
```

---

## Reasoning Operations

```text
filter()
rank()
compare_temporal()
```

These primitives can be composed to answer increasingly complex questions.

---

# 8. Operation Registry

The planner will not be allowed to invent arbitrary operations.

Instead, SatQuery will maintain an **Operation Registry**.

Conceptually:

```python
REGISTRY = {
    "retrieve_satellite": RetrieveSatelliteOperation,
    "retrieve_osm": RetrieveOSMOperation,

    "calculate_ndvi": CalculateNDVIOperation,
    "calculate_ndwi": CalculateNDWIOperation,
    "classify_landcover": LandCoverOperation,
    "detect_change": ChangeDetectionOperation,

    "buffer": BufferOperation,
    "intersection": IntersectionOperation,
    "clip": ClipOperation,
    "within_distance": DistanceOperation,

    "calculate_area": AreaOperation,
    "statistics": StatisticsOperation,
}
```

Each operation exposes:

```text
Operation Name
Input Type
Output Type
Parameter Schema
Validation Logic
Execution Handler
Metadata
```

This creates a controlled interface between the LLM and the execution system.

---

# 9. Base Operation Interface

All executable operations will follow a common interface.

Conceptually:

```python
class BaseOperation(ABC):

    @abstractmethod
    def validate(
        self,
        operation,
        context
    ):
        pass

    @abstractmethod
    def execute(
        self,
        operation,
        context
    ):
        pass
```

This ensures every operation can be:

1. Validated.
2. Executed.
3. Returned as a structured result.
4. Traced for evidence/provenance.

---

# 10. Execution Engine

The execution engine receives a validated `QueryPlan`.

Its responsibility is to:

1. Build the execution context.
2. Resolve dependencies.
3. Validate operations.
4. Execute operations.
5. Store results.
6. Generate evidence.
7. Return the final execution result.

Conceptually:

```text
QueryPlan
    ↓
Dependency Resolver
    ↓
Operation 1
    ↓
Operation 2
    ↓
Operation 3
    ↓
...
    ↓
Final Result
```

---

# 11. Dependency Graph

Operations form a **Directed Acyclic Graph (DAG)**.

For the hero query:

```text
             Sentinel-2 2024
                    │
                    ▼
                NDVI 2024
                    │
                    │
                    ├──────────────┐
                    │              │
                    ▼              │
             Vegetation Change     │
                    ▲              │
                    │              │
                NDVI 2026           │
                    ▲              │
                    │              │
             Sentinel-2 2026        │
                                   │
Major Roads                        │
    │                              │
    ▼                              │
Road Filter                        │
    │                              │
    ▼                              │
3 km Buffer                        │
    │                              │
    └──────────────┬───────────────┘
                   ▼
              Intersection
                   │
                   ▼
             Area Calculation
```

The dependency resolver determines the correct execution order.

Circular dependencies must be rejected.

---

# 12. Spatial and Temporal Reasoning

SatQuery's main differentiation comes from combining multiple analytical dimensions.

## Spatial Reasoning

Examples:

```text
within 3 km of roads
within 500 m of rivers
inside this region
intersects agricultural land
near urban areas
```

Implemented using operations such as:

```text
buffer
intersection
clip
within_distance
spatial_join
```

---

## Temporal Reasoning

Examples:

```text
between 2024 and 2026
since 2024
compared with last year
where vegetation decreased
where new construction occurred
```

Implemented using:

```text
temporal comparison
change detection
time-series analysis
```

---

## Multi-Step Reasoning

The real target capability is combining these operations.

For example:

```text
Vegetation Loss
       +
Major Roads
       +
3 km Distance
       +
Area Calculation
```

rather than simply answering:

```text
"What objects are in this image?"
```

---

# 13. Query Capability Levels

SatQuery is designed to evolve through increasing levels of reasoning.

## Level 1 — Direct Observation

Examples:

```text
What objects are visible in this area?

How much of this region is covered by water?

Identify agricultural areas.

Show major roads.
```

These establish the baseline.

---

## Level 2 — Spatial Reasoning

Examples:

```text
Show agricultural areas within 3 km of major roads.

Which buildings are within 500 m of this river?

What percentage of the area within 5 km of the city is urbanized?
```

---

## Level 3 — Temporal Reasoning

Examples:

```text
What has changed between 2024 and 2026?

Where has vegetation decreased the most?

Show areas where new construction occurred since 2024.
```

---

## Level 4 — Multi-Step Geospatial Reasoning

Example:

```text
Find areas where vegetation decreased between
2024 and 2026 that are within 3 km of major roads.
```

This is the current **hero query**.

---

## Level 5 — Conversational Reasoning

SatQuery should eventually support follow-up questions.

Example:

```text
User:
Show agricultural areas around this region.

System:
[Results]

User:
Now only show the ones within 3 km of rivers.

System:
[Filtered Results]

User:
Which of those experienced vegetation loss?

System:
[Further filtered results]

User:
How much area was affected?

System:
[Measurement]
```

The system therefore maintains the relationship between:

```text
Query
  ↓
Result
  ↓
Filter
  ↓
New Analysis
```

---

## Level 6 — Evidence & Explanation

Every important answer should ideally expose:

```text
Answer
Source
Acquisition Date
Analysis Performed
Operations
Parameters
Spatial Result
Confidence / Quality
```

The system should be able to explain **how it arrived at the result**.

---

# 14. Data Sources

SatQuery is designed around publicly accessible geospatial datasets and APIs.

### Primary Satellite Source

**Sentinel-2**

Used primarily for:

* Optical imagery
* Vegetation analysis
* Water analysis
* Land-cover analysis
* Temporal comparison
* Change detection

---

### Secondary Satellite Source

**Sentinel-1**

Used when radar information is advantageous, particularly for:

* Cloud-obstructed regions
* All-weather observations
* Surface monitoring
* Complementary SAR analysis

---

### Geospatial Data

**OpenStreetMap**

Used for features such as:

* Roads
* Buildings
* Infrastructure
* Other mapped geographic objects

---

### Additional Data Sources

The architecture is intentionally source-agnostic so additional datasets can be added later.

Potential sources include:

```text
NASA Earthdata
Copernicus datasets
DEM / elevation datasets
Hydrological datasets
Administrative boundaries
Land-cover datasets
Weather / environmental datasets
AIS / maritime data
```

The important architectural principle is:

> **The data source is an implementation detail of the operation, not something the user should need to understand.**

---

# 15. Evidence and Provenance

A major requirement of SatQuery is that answers should be **evidence-backed**.

The system should record information such as:

```text
Source:
Sentinel-2

Acquisition:
YYYY-MM-DD

Operation:
calculate_ndvi

Parameters:
...

Input:
...

Result:
...

Additional processing:
...

Confidence / Quality:
...
```

This prevents the language model from becoming the source of truth.

The LLM generates the plan.

The execution system generates the evidence.

---

# 16. Confidence Model

SatQuery should avoid presenting a meaningless single confidence number.

Confidence should eventually be decomposed into factors such as:

```text
Imagery Quality
       +
Model Confidence
       +
Spatial Accuracy
       +
Temporal Consistency
       +
Overall Result Quality
```

This makes the confidence information more useful and explainable.

---

# 17. Proposed Project Structure

```text
satquery-ai/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── query.py
│   │   ├── operation.py
│   │   ├── result.py
│   │   └── evidence.py
│   │
│   ├── planner/
│   │   ├── __init__.py
│   │   └── validator.py
│   │
│   ├── executor/
│   │   ├── __init__.py
│   │   ├── executor.py
│   │   ├── context.py
│   │   └── dependency.py
│   │
│   ├── registry/
│   │   ├── __init__.py
│   │   └── operations.py
│   │
│   ├── operations/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   │
│   │   ├── satellite/
│   │   │   ├── __init__.py
│   │   │   ├── retrieve.py
│   │   │   └── preprocess.py
│   │   │
│   │   ├── remote_sensing/
│   │   │   ├── __init__.py
│   │   │   ├── ndvi.py
│   │   │   ├── ndwi.py
│   │   │   └── change.py
│   │   │
│   │   └── gis/
│   │       ├── __init__.py
│   │       ├── buffer.py
│   │       ├── intersection.py
│   │       ├── distance.py
│   │       └── area.py
│   │
│   ├── evidence/
│   │   ├── __init__.py
│   │   └── builder.py
│   │
│   └── config/
│       ├── __init__.py
│       └── settings.py
│
├── tests/
│   ├── __init__.py
│   ├── operations/
│   ├── executor/
│   └── planner/
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

# 18. Development Roadmap

Development is intentionally divided into milestones.

## M1 — Execution Foundation

Goal:

> Prove that a structured query plan can be validated and executed through a controlled operation system.

Tasks:

* [x] Create GitHub repository
* [x] Initialize project
* [x] Create project directory structure
* [x] Create Python virtual environment
* [x] Install initial dependencies
* [x] Add `.gitignore`
* [ ] Implement schemas
* [ ] Implement `BaseOperation`
* [ ] Implement operation registry
* [ ] Implement execution context
* [ ] Implement dependency resolver
* [ ] Implement mock operations
* [ ] Implement mock executor
* [ ] Add unit tests

---

## M2 — Query Planner

Goal:

> Convert natural language into a validated `QueryPlan`.

Tasks:

* [ ] Query understanding
* [ ] Query planner
* [ ] Structured output
* [ ] Planner validation
* [ ] Operation compatibility checking
* [ ] Invalid-plan rejection
* [ ] Planner → Executor integration

---

## M3 — Real Geospatial Execution

Goal:

> Replace mock operations with real satellite and GIS processing.

Tasks:

* [ ] Sentinel-2 retrieval
* [ ] Sentinel-2 preprocessing
* [ ] NDVI
* [ ] NDWI
* [ ] Land-cover classification
* [ ] Change detection
* [ ] OpenStreetMap retrieval
* [ ] Buffer operations
* [ ] Intersection
* [ ] Distance calculations
* [ ] Area calculations

---

## M4 — Hero Query

Goal:

> Successfully execute the complete multi-step geospatial reasoning pipeline.

Target query:

```text
Find areas where vegetation decreased between
2024 and 2026 that are within 3 km of major roads.
```

Required pipeline:

```text
Natural Language
       ↓
Query Planner
       ↓
Sentinel-2 2024
       ↓
NDVI
       ↓
Sentinel-2 2026
       ↓
NDVI
       ↓
Temporal Difference
       ↓
Vegetation Loss
       ↓
OSM Major Roads
       ↓
3 km Buffer
       ↓
Spatial Intersection
       ↓
Area Calculation
       ↓
Map + Evidence
```

---

## M5 — Conversational Intelligence

Goal:

> Allow users to iteratively explore the same geographic context.

Tasks:

* [ ] Conversation state
* [ ] Query/result context
* [ ] Follow-up queries
* [ ] Result filtering
* [ ] Context-aware planning
* [ ] Query history

---

## M6 — Evidence & Explainability

Goal:

> Make every result traceable and understandable.

Tasks:

* [ ] Evidence builder
* [ ] Source metadata
* [ ] Acquisition dates
* [ ] Operation provenance
* [ ] Parameter display
* [ ] Confidence model
* [ ] Analysis explanation

---

## M7 — SIH Demonstration Layer

Goal:

> Convert the technical system into a polished 5-minute demonstration.

Potential interface:

```text
┌───────────────────────────────────────────────┐
│ SATQUERY                                      │
├───────────────────────────────────────────────┤
│                                               │
│ Ask a question about this region...           │
│                                               │
│ "Find vegetation loss near major roads."      │
│                                               │
├───────────────────────────────────────────────┤
│                                               │
│                 MAP                           │
│                                               │
│       Satellite + Analysis Overlays           │
│                                               │
├───────────────────────────────────────────────┤
│ Analysis                                      │
│                                               │
│ • Satellite imagery used                     │
│ • Temporal comparison                         │
│ • Road proximity analysis                     │
│ • Affected area                               │
│                                               │
└───────────────────────────────────────────────┘
```

---

# 19. Current Status

**Project phase: M1 — Execution Foundation**

The project has moved beyond the idea/proposal stage.

### Completed

```text
[x] SatQuery concept defined

[x] Core problem identified

[x] Architecture designed

[x] Query capability levels defined

[x] Hero query selected

[x] QueryPlan structure designed

[x] Operation primitive library defined

[x] Base operation interface designed

[x] Operation registry architecture designed

[x] Dependency/DAG execution model designed

[x] Evidence architecture defined

[x] Data-source strategy defined

[x] GitHub repository created

[x] Local repository initialized

[x] Project directory structure created

[x] Python virtual environment created

[x] Initial dependencies installed

[x] .gitignore created
```

### Currently Working On

```text
→ Initial Git commit / repository setup

→ M1 execution foundation
```

### Next Implementation Step

The immediate technical milestone is:

```text
Schemas
   ↓
BaseOperation
   ↓
Registry
   ↓
Dependency Resolver
   ↓
Mock Operations
   ↓
Executor
   ↓
Tests
```

The first implementation should **not** begin with satellite APIs or the LLM.

We will first prove that the execution architecture works using controlled/mock operations.

Once the execution engine is stable, real Sentinel-2 and OSM operations can be plugged into it.

---

# 20. Engineering Principles

SatQuery will follow several architectural principles throughout development.

### 1. LLM plans, code executes

The LLM determines intent and creates a plan.

Deterministic code performs the actual analysis.

---

### 2. Operations must be composable

Every operation should perform one semantic action.

```text
retrieve
calculate
filter
buffer
intersect
measure
```

These operations can then be composed into complex workflows.

---

### 3. No arbitrary LLM execution

The planner can only select operations exposed through the registry.

```text
LLM
 ↓
Validated QueryPlan
 ↓
Registry
 ↓
Known Operation
 ↓
Executor
```

---

### 4. Results must be reproducible

Given the same:

```text
AOI
+
input data
+
parameters
+
operations
```

the system should produce the same analytical result, subject to source-data updates.

---

### 5. Evidence is generated by execution

The LLM should never be trusted to invent:

* Satellite dates
* Data sources
* Calculated areas
* Statistical values
* Processing results

Those values must originate from the execution layer.

---

### 6. Modular data sources

The system should not be tightly coupled to a single satellite provider.

New data sources should be addable through operations without redesigning the planner.

---

### 7. Build the reasoning engine before the UI

The core product is:

```text
Natural Language
        ↓
Plan
        ↓
Execution
        ↓
Spatial Result
        ↓
Evidence
```

The frontend is a visualization layer on top of this engine.

---

# 21. Target Product

The final vision for SatQuery is:

> **Ask questions about the Earth the same way you ask questions to an AI assistant.**

But instead of generating an answer from language knowledge alone, SatQuery should:

```text
Understand the question
        ↓
Find the relevant geospatial data
        ↓
Determine the required analysis
        ↓
Execute the analysis
        ↓
Perform spatial / temporal reasoning
        ↓
Produce measurable results
        ↓
Show the result on a map
        ↓
Explain and provide evidence
```

The long-term goal is therefore not simply:

> **"ChatGPT for satellite images."**

It is:

> **"A natural-language execution engine for geospatial intelligence."**

---

# 22. Current Project State

```text
                 SATQUERY-AI
                      │
                      ▼
              ┌───────────────┐
              │   PROJECT     │
              │   DEFINITION  │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │  ARCHITECTURE │
              │    DESIGN     │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │   M1          │
              │   FOUNDATION  │
              └───────┬───────┘
                      │
              CURRENT POSITION
                      │
                      ▼
       ┌─────────────────────────────┐
       │ Repository + Structure      │
       │ Environment + Dependencies  │
       │ Git Configuration           │
       └──────────────┬──────────────┘
                      │
                      ▼
             NEXT: CORE ENGINE
                      │
                      ▼
       Schemas → Registry → DAG
                      │
                      ▼
                  Executor
                      │
                      ▼
              REAL GEO OPERATIONS
                      │
                      ▼
                HERO QUERY
                      │
                      ▼
              FULL SATQUERY MVP
```

---

## Vision

**SatQuery-AI** aims to bridge the gap between **natural-language AI** and **professional geospatial analysis**.

The system will allow users to ask high-level questions while the underlying engine handles the complexity of:

* Satellite data retrieval
* Remote sensing
* Computer vision
* GIS
* Spatial reasoning
* Temporal analysis
* Data fusion
* Evidence generation

The central architectural idea remains:

> **Natural language defines the intent.
> The planner defines the workflow.
> The execution engine performs the analysis.
> The evidence layer proves the result.**

### M1 — Execution Foundation Progress

#### Completed

* **Core Pydantic schemas**

  * `QueryPlan`
  * `Operation`
  * `DataInput`
  * `AOI`
  * `OutputSpec`
  * `OperationResult`
  * `ExecutionResult`
  * `Evidence`

* **Raster data abstraction**

  * Added `RasterData`
  * Added `RasterMetadata`
  * Supports NumPy-based raster arrays
  * Preserves CRS, dimensions, band information and raster metadata

* **Operation execution architecture**

  * Added `BaseOperation` interface
  * Added `OperationRegistry`
  * Added `ExecutionContext`
  * Added dependency resolution through topological sorting
  * Added execution engine through `Executor`

* **Runtime input support**

  * Execution context now supports runtime data injection
  * Enables operations to consume dynamically retrieved raster/vector data without coupling the planner to storage or retrieval implementations

* **Mock operations**

  * Added mock source, transform and combine operations
  * Added mock raster source for testing raster-processing pipelines

* **Remote sensing**

  * Implemented `NDVIOperation`
  * Supports configurable Red and NIR bands
  * Handles zero denominators safely
  * Returns NDVI as a `RasterData` result

* **Sentinel-2 retrieval**

  * Integrated Sentinel-2 L2A retrieval through Sentinel Hub / Copernicus Data Space
  * Configured CDSE OAuth authentication
  * Added configurable AOI, temporal range, cloud-coverage limit and output resolution
  * Currently retrieves B4 (Red) and B8 (NIR)
  * Converts API output into the internal `RasterData` representation

* **Integration testing**

  * Added executor → raster source → NDVI integration test
  * Added Sentinel-2 operation validation tests
  * Added runtime input tests
  * Added manual Sentinel-2 retrieval test script

#### Current M1 Status

```text
[✓] Core schemas
[✓] BaseOperation
[✓] Operation Registry
[✓] ExecutionContext
[✓] Runtime inputs
[✓] Dependency Resolver
[✓] Executor
[✓] Mock operations
[✓] RasterData abstraction
[✓] NDVI operation
[✓] Sentinel-2 retrieval
[ ] OSM retrieval
[ ] GIS buffer operation
[ ] GIS intersection operation
[ ] Distance/proximity operation
[ ] Area calculation
[ ] Hero query integration
```

### Current Verified Pipeline

The current implementation successfully executes the following pipeline:

```text
QueryPlan
    ↓
Dependency Resolver
    ↓
Executor
    ↓
Sentinel-2 Retrieval
    ↓
RasterData
    ↓
NDVI Operation
    ↓
NDVI Raster Result
```

A live Sentinel-2 retrieval has been verified against the Copernicus Data Space Ecosystem using Sentinel-2 L2A imagery.

The current verified output is:

```text
Shape: (2, 256, 256)
Bands: ['B4', 'B8']
CRS: EPSG:4326
Dtype: float32
```

### Next M1 Milestone

The next implementation target is **OSM retrieval and GIS reasoning**.

This will extend the execution engine from purely raster-based processing toward multi-source geospatial reasoning:

```text
Sentinel-2
    │
    ├── NDVI
    │
    └── Vegetation change
             │
             ▼
          Filter
             │
             ├──────────────┐
             │              │
             ▼              ▼
          OSM Roads     Road Filter
                            │
                            ▼
                       3 km Buffer
                            │
                            ▼
                     Spatial Intersection
                            │
                            ▼
                       Final Result
```

This will form the foundation for the SatQuery-AI hero query:

> **Find areas where vegetation decreased between 2024 and 2026 that are within 3 km of major roads.**

### M1 — GIS Reasoning Progress

#### Completed

- **OpenStreetMap retrieval**
  - Added OSM feature retrieval through OSMnx
  - Supports roads, buildings and waterways
  - Returns GeoDataFrame-based vector data
  - Preserves source CRS and feature metadata

- **Coordinate reference system projection**
  - Added `ProjectToCRSOperation`
  - Supports explicit CRS transformation for vector data
  - Enables metric-based spatial operations

- **Buffer operation**
  - Added `BufferOperation`
  - Supports distance-based spatial buffering
  - Requires projected input data for metric distances
  - Used for road-proximity reasoning

- **Spatial intersection**
  - Added `IntersectionOperation`
  - Computes intersections between vector layers
  - Explicitly validates CRS compatibility
  - Supports runtime inputs through the execution context

- **Area calculation**
  - Added `AreaOperation`
  - Calculates total affected area from vector geometries
  - Requires a projected CRS with metric units
  - Returns area in both m² and km²

- **Full GIS pipeline integration**
  - Verified the complete GIS execution chain through the `Executor`
  - Runtime vegetation-loss polygons can be combined with live/mock OSM road data
  - Pipeline now supports the core spatial reasoning required by the hero query

#### Verified GIS Pipeline

```text
OSM Roads
    ↓
Project to UTM
    ↓
3 km Buffer
    ↓
Vegetation-loss Polygons
    ↓
Spatial Intersection
    ↓
Area Calculation
    ↓
Affected Area

### 11.4.2 — Deterministic Hero Query Integration

Implemented and validated the first complete end-to-end execution path for the SatQuery hero query:

> **Find areas where vegetation decreased between 2024 and 2026 that are within 3 km of major roads.**

#### Implemented Pipeline

```text
Sentinel-2 2024
      │
      ├──→ NDVI 2024 ───────┐
      │                     │
Sentinel-2 2026             ↓
      │              Temporal Difference
      └──→ NDVI 2026 ───────┘
                            │
                            ↓
                     Vegetation Loss
                            │
                            ↓
                    Raster Polygonize
                            │
                            ↓
                      Project to UTM
                            │
OSM Major Roads             │
      │                     │
      ↓                     │
 Project to UTM             │
      │                     │
      ↓                     │
  3 km Buffer ──────────────┘
                            │
                            ↓
                       Intersection
                            │
                            ↓
                     Area Calculation
```

#### Integration Work Completed

* Added deterministic hero-query integration test.
* Added synthetic Sentinel-2 raster inputs for 2024 and 2026.
* Added synthetic OSM road geometry.
* Validated runtime input injection for raster and vector data.
* Updated `ProjectToCRSOperation` to support runtime `GeoDataFrame` inputs.
* Preserved existing `ProjectToCRSOperation` validation and metadata contracts.
* Validated CRS transformation to EPSG:32643.
* Validated vegetation-change detection.
* Validated vegetation-loss extraction.
* Validated raster-to-polygon conversion.
* Validated 3 km road buffering.
* Validated spatial intersection.
* Validated final affected-area calculation.
* Confirmed the complete operation dependency chain executes through the `Executor`.

#### Validation

```text
pytest -q
104 passed
```

Ruff:

```text
ruff check .
All checks passed
```

Rasterio emits `PendingDeprecationWarning` messages originating from its internal `Affine` multiplication; these do not affect test results.

#### Checkpoint Status

* [x] Deterministic hero query executes end-to-end
* [x] Raster runtime inputs supported
* [x] Vector runtime inputs supported
* [x] NDVI 2024/2026
* [x] Temporal vegetation change
* [x] Vegetation-loss extraction
* [x] Raster polygonization
* [x] CRS projection
* [x] 3 km road buffer
* [x] Spatial intersection
* [x] Area calculation
* [x] Full test suite passing
* [x] Ruff clean

**Checkpoint: 11.4.2 COMPLETE**

### 11.5.2 — OSM Retrieval & Major-Road Filtering

Implemented the OpenStreetMap retrieval layer for geospatial reasoning.

#### Implemented

- Added OSM feature retrieval through OSMnx.
- Added support for:
  - Roads
  - Buildings
  - Waterways
- Added bounding-box validation.
- Added supported feature-type validation.
- Added semantic filtering for major roads.
- Major road classes currently include:
  - motorway
  - motorway_link
  - trunk
  - trunk_link
  - primary
  - primary_link
  - secondary
  - secondary_link
- Added handling for OSM `highway` values represented as either strings or lists.
- Added explicit failure handling when no OSM features are returned.
- Added explicit failure handling when no major roads are found.
- Preserved OSM source metadata and feature counts in `OperationResult`.

#### Why This Matters

The hero query requires reasoning about proximity to **major roads**, rather than arbitrary OSM road features.

The retrieval layer now converts:

```text
Natural-language concept:
"major roads"
        ↓
OSM highway features
        ↓
Semantic road-class filtering
        ↓
Major-road GeoDataFrame

### 11.5.3 — Retrieval Operations Integrated into Hero Pipeline

Completed integration of external data retrieval into the deterministic hero execution graph.

#### Changes

- Added deterministic mock Sentinel-2 retrieval operation for tests.
- Added deterministic mock OSM retrieval operation for tests.
- Updated the test operation registry so retrieval operations can be mocked without changing production implementations.
- Updated the hero `QueryPlan` to explicitly execute:
  - `get_satellite_imagery` for 2024 Sentinel-2 data.
  - `get_satellite_imagery` for 2026 Sentinel-2 data.
  - `get_osm_features` for major-road retrieval.
- Retrieval responses are now converted into `OperationResult` objects before downstream processing.
- NDVI operations consume Sentinel-2 retrieval results through operation dependencies.
- OSM results flow through CRS projection before metric buffering and spatial intersection.
- Runtime inputs are now used as deterministic mock retrieval responses rather than bypassing the retrieval layer.
- Added retrieval-operation override support to the test registry so individual integration tests can explicitly exercise production retrieval implementations when required.

#### Hero Execution Graph

```text
Sentinel-2 2024 ──→ NDVI 2024 ──┐
                                │
Sentinel-2 2026 ──→ NDVI 2026 ──┤
                                ↓
                         Temporal Difference
                                ↓
                         Vegetation Loss
                                ↓
                           Polygonize
                                ↓
                         Project to CRS
                                │
OSM Major Roads ──→ Project to CRS
                                ↓
                           3 km Buffer
                                ↓
                           Intersection
                                ↓
                              Area

+## 11.5.4 — Evidence Generation
+
+Implemented the evidence/provenance layer for executed QueryPlans.
+
+### Completed
+
+- Added `EvidenceBuilder` in `app/evidence/builder.py`
+- Evidence is generated from the executed `Operation` and its `OperationResult`
+- Evidence captures:
+  - data source
+  - source type
+  - acquisition date when available
+  - operation type
+  - operation parameters
+  - operation description when available
+- Wired evidence generation into `Executor`
+- Evidence is attached only after successful operation execution
+- Missing provenance metadata falls back to safe defaults rather than invented values
+- Hero pipeline now produces evidence for all executed operations
+- Verified Sentinel-2 and OSM retrieval provenance in the hero pipeline
+- Added focused unit and executor tests for evidence generation
+
+### Validation
+
+- Evidence builder tests passing
+- Executor evidence test passing
+- Hero pipeline evidence assertions passing
+- Evidence count matches the number of executed operations
+- No external API calls are required by evidence tests
+
+**Status: Complete**

+## 11.5.5 — API Endpoint
+
+Implemented the FastAPI API layer for executing validated QueryPlans.
+
+### Completed
+
+- Added FastAPI application entry point in `app/main.py`
+- Added `POST /query` endpoint in `app/api/routes.py`
+- API endpoint uses the existing `Executor` and production operation registry
+- Added dependency injection for the Executor
+- Added API-specific serialization for execution results
+- Raster results expose bands and geospatial metadata without returning raw NumPy arrays
+- Vector results are serialized through GeoJSON-compatible `__geo_interface__`
+- Evidence is returned as JSON-serializable provenance records
+- API execution does not duplicate planner or executor logic
+- Added deterministic API tests using the mock operation registry
+- Added FastAPI/Uvicorn/httpx2 dependencies to `requirements.txt`
+- Fixed FastAPI `Depends` linting with an explicit Ruff `B008` suppression
+
+### Validation
+
+- API endpoint test passing
+- Full test suite passing
+- Ruff checks passing
+- API tests require no external Sentinel-2 or OSM services
+- Production registry is used by the API outside of tests
+
+**Status: Complete**