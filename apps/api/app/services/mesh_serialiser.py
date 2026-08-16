import logging
from typing import Any

logger = logging.getLogger(__name__)


def serialise_mesh(shape: Any) -> dict:
    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.TopAbs import TopAbs_FACE
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.TopLoc import TopLoc_Location

    BRepMesh_IncrementalMesh(shape, 0.1, False, 0.5, True).Perform()

    vertices: list[float] = []
    normals: list[float] = []
    indices: list[int] = []
    idx_offset = 0

    min_x = min_y = min_z = float("inf")
    max_x = max_y = max_z = float("-inf")

    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = explorer.Current()
        location = TopLoc_Location()
        triangulation = BRep_Tool.Triangulation(face, location)

        # pythonocc-core 7.9 returns None when no triangulation; older versions had IsNull()
        if triangulation is None:
            explorer.Next()
            continue

        try:
            nb_nodes = triangulation.NbNodes()
            nb_triangles = triangulation.NbTriangles()
        except Exception:
            explorer.Next()
            continue

        if nb_nodes == 0 or nb_triangles == 0:
            explorer.Next()
            continue

        for i in range(1, nb_nodes + 1):
            p = triangulation.Node(i)
            x, y, z = p.X(), p.Y(), p.Z()
            vertices.extend([x, y, z])
            min_x = min(min_x, x); min_y = min(min_y, y); min_z = min(min_z, z)
            max_x = max(max_x, x); max_y = max(max_y, y); max_z = max(max_z, z)
            try:
                if triangulation.HasNormals():
                    n = triangulation.Normal(i)
                    normals.extend([n.X(), n.Y(), n.Z()])
                else:
                    normals.extend([0.0, 0.0, 1.0])
            except Exception:
                normals.extend([0.0, 0.0, 1.0])

        for i in range(1, nb_triangles + 1):
            tri = triangulation.Triangle(i)
            n1, n2, n3 = tri.Get()
            indices.extend([n1 - 1 + idx_offset, n2 - 1 + idx_offset, n3 - 1 + idx_offset])

        idx_offset += nb_nodes
        explorer.Next()

    if not vertices:
        logger.warning("Mesh serialisation produced no vertices")

    bounding_box = {
        "min": [min_x if min_x != float("inf") else 0, min_y if min_y != float("inf") else 0, min_z if min_z != float("inf") else 0],
        "max": [max_x if max_x != float("-inf") else 100, max_y if max_y != float("-inf") else 100, max_z if max_z != float("-inf") else 100],
    }

    logger.info(f"Mesh: {len(vertices)//3} vertices, {len(indices)//3} triangles")
    return {"vertices": vertices, "indices": indices, "normals": normals, "bounding_box": bounding_box}


def serialise_mesh_to_obj(shape: Any) -> str:
    mesh_data = serialise_mesh(shape)
    vertices = mesh_data["vertices"]
    indices = mesh_data["indices"]
    normals = mesh_data["normals"]

    lines = ["# VexForm — Lower Valve Body", "o LowerValveBody", ""]
    for i in range(0, len(vertices), 3):
        lines.append(f"v {vertices[i]:.6f} {vertices[i+1]:.6f} {vertices[i+2]:.6f}")
    for i in range(0, len(normals), 3):
        lines.append(f"vn {normals[i]:.6f} {normals[i+1]:.6f} {normals[i+2]:.6f}")
    lines.append("")
    for i in range(0, len(indices), 3):
        a, b, c = indices[i] + 1, indices[i+1] + 1, indices[i+2] + 1
        if normals:
            lines.append(f"f {a}//{a} {b}//{b} {c}//{c}")
        else:
            lines.append(f"f {a} {b} {c}")

    return "\n".join(lines) + "\n"
