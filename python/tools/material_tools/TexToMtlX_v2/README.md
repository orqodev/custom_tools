TexToMtlX v2
============

Overview
- TexToMtlX v2 is a new, non-destructive rewrite of our texture → MaterialX creation tool.
- It lives alongside the legacy tools; nothing in TexToMtlX_legacy is modified.
- v2 centralizes configuration and colorspace logic, standardizes UDIM handling, and introduces optional multi-renderer hooks.

Repo Layout
/tools/material_tools/
  TexToMtlX_legacy/             # read-only references (kept intact)
    tex_to_mtlx.py
    KB3D_converter.py
  TexToMtlX_v2/                 # active development
    textomtlx_tool.py           # main UI tool (this version)
    mtx_cs_resolver.py          # colorspace/semantic + UDIM helpers
    txmtlx_config.py            # centralized knobs and constants
    README.md                   # this file

Highlights in v2
- Procedural colorspace: guess_semantics_and_colorspace() determines signature and filecolorspace per texture.
- Shared UDIM handling: single regex (1001–2999) to detect/replace with <UDIM>; mtlxtiledimage for UDIM, mtlximage otherwise.
- TX conversion: bounded concurrency via WORKER_FRACTION and --newer flag.
- $JOB normalization: case-insensitive replacement of project root, safe and standardized.
- Multi-renderer hooks: Karma by default; optional Arnold path if HtoA detected (minimal MVP).
- Optional features off by default: /stage material library creation, collect node, displacement remap/scale.
- Emission toggle: emission enabled automatically when emission map is connected.
- Bump/Normal: honors UDIM choice and uses place2d flow for non-UDIM textures.
- Report dialog after batch: shows successes and failures with error text.

Install / Use
1) Place this folder under your Houdini site packages (already present in this repository layout).
2) From a Python Shell or shelf tool inside Houdini, run:
   from custom_tools.scripts.python.tools.material_tools.TexToMtlX_v2.textomtlx_tool import show_ttmx_v2
   show_ttmx_v2()
3) Pick a material library (/mat, matnet, or materiallibrary), select folders with textures, select materials to create, and click Create.

Migration notes (v1 → v2)
- v2 preserves the stable subnet and MaterialX-first flow but moves colorspace and UDIM logic to shared helpers.
- Name sanitization is simplified and configurable via UI; legacy drop-tokens are not hardcoded.
- TX conversion is parallelized more safely (submit-all then as_completed).
- Optional features (Arnold, /stage matlib, collect, displacement remap) are opt-in to avoid breaking older pipelines.

Feature toggles and defaults
- Karma: ON by default.
- Arnold: Auto-enabled only if HtoA is detected in hou.houdiniPath(); otherwise disabled.
- /stage Material Library: OFF by default.
- Collect Node: OFF by default.
- Displacement Remap: OFF by default; Displacement Scale defaults to 0.1.
- Convert to TX: OFF by default.

Known limitations
- Arnold path is an MVP: basic standard_surface hookup, simple colorspace mapping, no UDIM tiling node (Arnold handles UDIM tokens in file path).
- Filename parsing relies on token presence; highly custom naming may require extending TEXTURE_TYPE tokens.
- No headless/batch CLI included yet.
- No automatic detection of material destination context (user picks explicitly).

Test Matrix (manual)
- Non-UDIM LDR (png/jpg): Basecolor/Rough/Metal/Normal → signature/colorspace set; emission enables when emission map exists.
- UDIM HDR (exr/tif): Color → scene_linear; data/normal → raw; path shows <UDIM>; mtlxtiledimage used.
- TX: .tx outputs generated only when source newer; responsive logs; bounded workers.
- $JOB normalization: works case-insensitively when folder under JOB.
- Arnold present: builds Arnold network and, if Karma also on and Collect option checked, a collect node referencing both.
- Report dialog shows success and failures.

Support
File issues or requests via your team’s preferred channel. Contributions should be backward compatible and keep optional features disabled by default.
