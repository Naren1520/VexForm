// ── Generic shape parameter types ─────────────────────────────────────────────

/** A single parameter field returned by the backend schema. */
export interface FieldDef {
  key: string;
  label: string;
  unit: string;           // "mm", "°", "" etc.
  field_type: 'float' | 'int' | 'string';
  min_val: number | null;
  max_val: number | null;
  description: string;
}

/** A collapsible section of fields in the param panel. */
export interface SectionDef {
  label: string;
  keys: string[];
}

/** Full parameter schema for a shape type — returned by /extract and GET /shapes/:type/schema */
export interface ShapeSchema {
  shape_type: string;
  display_name: string;
  fields: FieldDef[];
  sections: SectionDef[];
  feature_tree_order: string[];
  reference_values: Record<string, number | string | null>;
}

/** Generic params dict — keys are field names, values are numbers, strings or null */
export type ShapeParams = Record<string, number | string | null>;

// ── Field status for the review form ─────────────────────────────────────────

export type ParamFieldStatus =
  | 'ai_match'       // AI value within 20% of reference → blue #4488FF
  | 'ai_deviation'   // AI value deviates >20% from reference → red #FF4444
  | 'ai_null'        // AI returned null, pre-filled with reference → grey #888888
  | 'user_edited';   // User has overridden the value

export interface ParamFieldState {
  value: number | string;
  status: ParamFieldStatus;
}

/** Dynamic form state — keyed by field name */
export type ParamFormState = Record<string, ParamFieldState>;

// ── Mesh payload from backend ─────────────────────────────────────────────────

export interface MeshPayload {
  /** Flat float array: [x0,y0,z0, x1,y1,z1, ...] in mm */
  vertices: number[];
  /** Flat uint32 array: triangle indices */
  indices: number[];
  /** Flat float array: per-vertex normals [nx0,ny0,nz0, ...] */
  normals: number[];
  /** Bounding box in mm for scale bar calculation */
  boundingBox: {
    min: [number, number, number];
    max: [number, number, number];
  };
}

// ── Feature tree ──────────────────────────────────────────────────────────────

export type FeatureStatus = 'success' | 'failed' | 'pending';

export interface FeatureNode {
  id: string;
  label: string;
  status: FeatureStatus;
  /** Face/edge identifiers for highlight in viewport */
  geometryRef?: string;
  confidence?: number;
  outputType?: 'wire' | 'face' | 'solid' | 'compound' | 'surface';
  topology?: Record<string, unknown>;
  evidence?: Record<string, unknown>[];
}

export interface CADFeature {
  id: string;
  type: string;
  parameters: Record<string, unknown>;
  depends_on?: string[];
  confidence?: number;
  label?: string;
}

export interface CADModel {
  version: string;
  units: string;
  coordinate_system?: Record<string, unknown>;
  sketches?: Record<string, unknown>[];
  features: CADFeature[];
  dimensions?: Record<string, unknown>[];
  constraints?: Record<string, unknown>[];
  metadata?: Record<string, unknown>;
  views?: { id: string; view_type: string; features?: string[]; confidence?: number }[];
  blueprint_confidence?: number;
  overall_confidence?: number;
}

// ── API request / response contracts ─────────────────────────────────────────

export interface ExtractResponse {
  shape_type: string;
  params: ShapeParams;
  schema: ShapeSchema;
  source: 'gemini' | 'fallback';
  elapsed_ms: number;
  cad_ir?: CADModel;
  review_state?: 'EXTRACTING' | 'EXTRACTED' | 'NEEDS_REVIEW' | 'VALIDATED' | 'GENERATING' | 'GENERATED' | 'FAILED';
  uncertainties?: { code: string; message: string; feature_ids?: string[]; confidence?: number }[];
}

export interface GenerateRequest {
  shape_type: string;
  params: ShapeParams;
}

export interface GenerateResponse {
  mesh: MeshPayload;
  featureTree: FeatureNode[];
  elapsed_ms: number;
}

export interface ValidationError {
  constraint: string;
  parameter: string | string[];
  submitted_value: number | number[];
  expected_bound: string;
}

export interface ValidationErrorResponse {
  errors: ValidationError[];
}

export interface ExportErrorResponse {
  error: string;
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | 'error';
  opencascade_version: string;
}

// ── Toast ─────────────────────────────────────────────────────────────────────

export interface Toast {
  id: string;
  message: string;
  level: 'info' | 'error';
  createdAt: number;
}

// ── Legacy LowerValveBodyParams (kept for reference / backwards compat) ───────
// The frontend now uses ShapeParams (generic dict) at runtime.
// This interface documents the Lower Valve Body field names.
export interface LowerValveBodyParams {
  overall_height: number;
  outer_body_diameter: number;
  main_bore_upper_diameter: number;
  main_bore_lower_inner_diameter: number;
  main_bore_lower_outer_step_diameter: number;
  side_port_bore_diameter: number;
  top_flange_outer_diameter: number;
  top_flange_bolt_hole_diameter: number;
  top_flange_bolt_hole_depth: number;
  top_flange_bolt_hole_count: number;
  top_flange_counterbore_diameter: number;
  top_flange_counterbore_depth: number;
  bottom_flange_outer_diameter: number;
  bottom_flange_bolt_circle_diameter: number;
  bottom_flange_outer_flange_diameter: number;
  bottom_flange_bolt_hole_diameter: number;
  bottom_flange_bolt_hole_count: number;
  bottom_flange_counterbore_diameter: number;
  bottom_flange_counterbore_depth: number;
  side_port_flange_outer_diameter: number;
  side_port_bolt_hole_diameter: number;
  side_port_bolt_hole_spacing: number;
  side_port_angle_degrees: number;
  side_port_offset_from_top: number;
  unspecified_fillet_radius: number;
  internal_step_chamfer: number;
  other_chamfer: number;
  material: string;
}

// Partial version returned by AI extractor (values may be null)
export type ExtractedParams = {
  [K in keyof LowerValveBodyParams]: LowerValveBodyParams[K] | null;
};
