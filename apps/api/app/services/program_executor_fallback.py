"""Pure-Python fallback executor for construction programs (no OCC required).

Interprets the same program format as program_executor.py but uses
the MeshBuilder from generic_fallback.py.
"""
from __future__ import annotations
import math
import logging
from app.services.generic_fallback import MeshBuilder, _cylinder, _box

logger = logging.getLogger(__name__)


def execute_program_fallback(program: list[dict]) -> tuple[dict, list[dict]]:
    """Execute a construction program using pure-Python mesh primitives.

    NOTE: This does NOT do real Boolean operations — it just merges/approximates.
    It's purely for environments where OCC is not installed.
    """
    mb = MeshBuilder()
    tree: list[dict] = []

    for i, step in enumerate(program):
        op = step.get("op", "").lower().strip()
        label = step.get("label", op)
        step_id = f"step_{i:02d}_{op}"

        x = float(step.get("x", 0))
        y = float(step.get("y", 0))
        z = float(step.get("z", 0))

        try:
            if op in ("cylinder", "add_cylinder"):
                r = float(step["r"]); h = float(step["h"])
                mb.merge(_cylinder(x, y, z, z + h, r))
                tree.append({"id": step_id, "label": label, "status": "success"})

            elif op in ("cut_cylinder",):
                # Can't do real boolean — render as inner cylinder (approximation)
                r = float(step["r"]); h = float(step["h"])
                inner = _cylinder(x, y, z, z + h, r * 0.8)
                # Don't merge — just skip for visual (booleans need OCC)
                tree.append({"id": step_id, "label": label, "status": "pending"})

            elif op in ("box", "add_box"):
                sx = float(step["sx"]); sy = float(step["sy"]); sz = float(step["sz"])
                centered = bool(step.get("centered", True))
                ox = x - sx/2 if centered else x
                oy = y - sy/2 if centered else y
                mb.merge(_box(ox, oy, z, ox + sx, oy + sy, z + sz))
                tree.append({"id": step_id, "label": label, "status": "success"})

            elif op in ("cut_box", "cut_sphere"):
                tree.append({"id": step_id, "label": label, "status": "pending"})

            elif op == "sphere":
                r = float(step["r"])
                mb.merge(_cylinder(x, y, z - r, z + r, r))  # sphere approximated as cylinder
                tree.append({"id": step_id, "label": label, "status": "success"})

            elif op == "bolt_circle":
                r_hole = float(step["r_hole"])
                count = int(step["count"])
                r_circle = float(step["r_circle"])
                depth = float(step.get("depth", 10))
                for j in range(count):
                    a = j * 2 * math.pi / count
                    hx = x + r_circle * math.cos(a)
                    hy = y + r_circle * math.sin(a)
                    mb.merge(_cylinder(hx, hy, z, z + depth * 0.3, r_hole * 0.6))
                tree.append({"id": step_id, "label": label, "status": "pending"})

            elif op in ("fillet", "chamfer"):
                tree.append({"id": step_id, "label": label, "status": "pending"})

            else:
                tree.append({"id": step_id, "label": label, "status": "failed"})

        except Exception as exc:
            logger.warning(f"Fallback step {i} '{op}' failed: {exc}")
            tree.append({"id": step_id, "label": label, "status": "failed"})

    if not mb.verts:
        # Emergency fallback: a plain cylinder
        mb.merge(_cylinder(0, 0, 0, 100, 50))
        tree.append({"id": "emergency_fallback", "label": "Emergency Body", "status": "failed"})

    return mb.to_mesh_data(), tree
