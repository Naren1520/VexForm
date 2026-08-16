"""Tessellate an OCC TopoDS_Shape into a flat mesh payload for Three.js."""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def serialise_mesh(shape: Any) -> dict:
    """Tessellate the solid and return a dict with flat vertex/index/normal arrays.

    Uses BRepMesh_IncrementalMesh with 0.1mm linear deflection.
    Returns:
        {
          "vertices": [x0,y0,z0, x1,y1,z1, ...],
          "indices":  [i0,i1,i2, ...],
          "normals":  [nx0,ny0,nz0, ...],
          "bounding_box": {"min": [x,y,z], "max": [x,y,z]}
        }
    """
    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.TopAbs import TopAbs_FACE
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.TopLoc import TopLoc_Location

    # Tessellate with 0.1mm linear deflection and 0.5 rad angular deflection
    mesh = BRepMesh_IncrementalMesh(shape, 0.1, False, 0.5, True)
    mesh.Perform()

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

        if triangulation is not None and not triangulation.IsNull():
            nb_nodes = triangulation.NbNodes()
            nb_triangles = triangulation.NbTriangles()

            # Get the face transformation matrix
            trsf = location.IsIdentity() and None or location.IsIdentity()
            # Apply location transform to nodes
            from OCC.Core.BRep import BRep_Tool as _BT
            from OCC.Core.BRepAdaptor import BRepAdaptor_Surface

            for i in range(1, nb_nodes + 1):
                node = triangulation.Node(i)
                # Apply location
                if not location.IsIdentity():
                    node.Transform(location.IsIdentity() or location.IsIdentity())

                # Direct node coordinates (in the face's local frame)
                p = node
                x, y, z = p.X(), p.Y(), p.Z()

                vertices.extend([x, y, z])

                # Bounding box update
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                min_z = min(min_z, z)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                max_z = max(max_z, z)

                # Normals (per-node if available, else zero)
                try:
                    if triangulation.HasNormals():
                        nx, ny, nz = triangulation.Normal(i).Coord()
                    else:
                        nx, ny, nz = 0.0, 0.0, 1.0
                except Exception:
                    nx, ny, nz = 0.0, 0.0, 1.0
                normals.extend([nx, ny, nz])

            for i in range(1, nb_triangles + 1):
                tri = triangulation.Triangle(i)
                n1, n2, n3 = tri.Get()
                # Account for face orientation
                indices.extend([
                    n1 - 1 + idx_offset,
                    n2 - 1 + idx_offset,
                    n3 - 1 + idx_offset,
                ])

            idx_offset += nb_nodes

        explorer.Next()

    if not vertices:
        logger.warning("Mesh serialisation produced no vertices — shape may not have been tessellated")

    bounding_box = {
        "min": [min_x, min_y, min_z],
        "max": [max_x, max_y, max_z],
    }

    logger.info(
        f"Mesh serialised: {len(vertices)//3} vertices, "
        f"{len(indices)//3} triangles"
    )

    return {
        "vertices": vertices,
        "indices": indices,
        "normals": normals,
        "bounding_box": bounding_box,
    }


def serialise_mesh_to_obj(shape: Any) -> str:
    """Serialise the mesh as a Wavefront OBJ string."""
    mesh_data = serialise_mesh(shape)
    vertices = mesh_data["vertices"]
    indices = mesh_data["indices"]
    normals = mesh_data["normals"]

    lines = ["# VexForm — Lower Valve Body", "o LowerValveBody", ""]

    # Vertices
    for i in range(0, len(vertices), 3):
        lines.append(f"v {vertices[i]:.6f} {vertices[i+1]:.6f} {vertices[i+2]:.6f}")

    # Normals
    for i in range(0, len(normals), 3):
        lines.append(f"vn {normals[i]:.6f} {normals[i+1]:.6f} {normals[i+2]:.6f}")

    lines.append("")

    # Faces (1-indexed)
    for i in range(0, len(indices), 3):
        a, b, c = indices[i] + 1, indices[i+1] + 1, indices[i+2] + 1
        if normals:
            lines.append(f"f {a}//{a} {b}//{b} {c}//{c}")
        else:
            lines.append(f"f {a} {b} {c}")

    return "\n".join(lines) + "\n"
