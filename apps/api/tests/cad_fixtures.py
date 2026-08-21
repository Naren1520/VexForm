from app.cad.ir import CADFeature, CADModel, GeometryEntity, Sketch


def rectangle_sketch(sketch_id: str = "sketch_01") -> Sketch:
    points = [([0, 0], [50, 0]), ([50, 0], [50, 30]), ([50, 30], [0, 30]), ([0, 30], [0, 0])]
    return Sketch(
        id=sketch_id,
        plane="XY",
        closed=True,
        entities=[GeometryEntity(type="line", parameters={"start": start, "end": end}) for start, end in points],
    )


def extruded_rectangle_model() -> CADModel:
    sketch = rectangle_sketch()
    return CADModel(
        sketches=[sketch],
        features=[CADFeature(id="base", type="extrude", depends_on=[sketch.id], parameters={"distance": 40})],
    )


def complex_prismatic_model() -> CADModel:
    return CADModel(features=[
        CADFeature(id="base", type="box", parameters={"sx": 100, "sy": 60, "sz": 10}),
        CADFeature(id="hole", type="hole", depends_on=["base"], parameters={"diameter": 10, "depth": 10}),
        CADFeature(id="fillet", type="fillet", depends_on=["hole"], parameters={"radius": 2}),
        CADFeature(id="chamfer", type="chamfer", depends_on=["fillet"], parameters={"size": 1}),
    ])


def revolved_shaft_model() -> CADModel:
    return CADModel(features=[
        CADFeature(id="profile", type="sketch", parameters={
            "plane": "XY", "closed": True,
            "entities": [
                {"type": "line", "start": [0, 0], "end": [20, 0]},
                {"type": "line", "start": [20, 0], "end": [20, 80]},
                {"type": "line", "start": [20, 80], "end": [0, 80]},
                {"type": "line", "start": [0, 80], "end": [0, 0]},
            ],
        }),
        CADFeature(id="shaft", type="revolve", depends_on=["profile"], parameters={
            "axis": {"origin": [0, 0, 0], "direction": [0, 1, 0]}, "angle": 360,
        }),
    ])


def swept_pipe_model() -> CADModel:
    return CADModel(features=[
        CADFeature(id="profile", type="sketch", parameters={
            "plane": "YZ", "closed": True,
            "entities": [{"type": "circle", "center": [0, 0], "radius": 5}],
        }),
        CADFeature(id="path", type="sketch", parameters={
            "plane": "XZ", "closed": False,
            "entities": [{"type": "line", "start": [0, 0], "end": [0, 100]}],
        }),
        CADFeature(id="pipe", type="sweep", depends_on=["profile", "path"]),
    ])


def lofted_component_model() -> CADModel:
    sections = []
    for index, size in enumerate((20, 30, 40), start=1):
        section_id = f"section_{index}"
        sections.append(CADFeature(id=section_id, type="sketch", parameters={
            "plane": "XY", "closed": True,
            "entities": [{"type": "circle", "center": [0, 0], "radius": size}],
        }))
    sections.append(CADFeature(id="loft", type="loft", depends_on=["section_1", "section_2", "section_3"]))
    return CADModel(features=sections)


def valve_generic_cad_ir_model() -> CADModel:
    """Deterministic valve-like fixture expressed only with generic CAD-IR features."""
    return CADModel(
        metadata={"part_name": "Valve compatibility fixture", "source": "deterministic_blueprint_fixture"},
        views=[
            {"id": "front", "view_type": "front", "features": ["body", "top_flange", "bottom_flange"]},
            {"id": "section", "view_type": "section", "features": ["main_bore"]},
        ],
        features=[
            CADFeature(id="body", type="cylinder", parameters={"r": 18, "h": 118}),
            CADFeature(id="top_flange", type="cylinder", depends_on=["body"], parameters={"r": 40, "h": 8, "z": 118}),
            CADFeature(id="bottom_flange", type="cylinder", depends_on=["top_flange"], parameters={"r": 40, "h": 6, "z": -6}),
            CADFeature(id="main_bore", type="hole", depends_on=["bottom_flange"], parameters={"diameter": 28, "depth": 130, "z": -7}),
        ],
    )


def generic_mechanical_models() -> list[CADModel]:
    """Five mechanically different graphs using only the generic CAD-IR vocabulary."""
    return [
        CADModel(features=[CADFeature(id="bracket", type="box", parameters={"sx": 100, "sy": 60, "sz": 8})]),
        CADModel(features=[
            CADFeature(id="flange", type="cylinder", parameters={"r": 50, "h": 12}),
            CADFeature(id="bore", type="hole", depends_on=["flange"], parameters={"diameter": 30, "depth": 12}),
        ]),
        CADModel(features=[CADFeature(id="shaft", type="cylinder", parameters={"r": 15, "h": 120})]),
        CADModel(features=[
            CADFeature(id="housing", type="box", parameters={"sx": 120, "sy": 80, "sz": 60}),
            CADFeature(id="bearing_bore", type="hole", depends_on=["housing"], parameters={"diameter": 40, "depth": 60, "x": 0, "y": 0, "z": 0}),
        ]),
        CADModel(features=[
            CADFeature(id="pulley", type="torus", parameters={"r_major": 35, "r_minor": 8}),
            CADFeature(id="hub", type="cylinder", depends_on=["pulley"], parameters={"r": 30, "h": 20, "z": -10}),
        ]),
    ]
