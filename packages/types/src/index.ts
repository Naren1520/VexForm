// ── Parameter types ───────────────────────────────────────────────────────────

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

// Partial version returned by AI_Extractor (values may be null)
export type ExtractedParams = {
  [K in keyof LowerValveBodyParams]: LowerValveBodyParams[K] | null;
};

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

export type ParamFormState = {
  [K in keyof LowerValveBodyParams]: ParamFieldState;
};

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
}

export const FEATURE_TREE_ORDER: readonly string[] = [
  'base_cylinder',
  'top_flange_extrusion',
  'bottom_flange_extrusion',
  'side_port_boss',
  'upper_bore_cut',
  'lower_bore_cut',
  'side_port_bore_cut',
  'top_bolt_holes_cut',
  'top_counterbores_cut',
  'bottom_bolt_holes_cut',
  'bottom_counterbores_cut',
  'side_port_bolt_holes_cut',
  'fillets',
  'chamfers',
] as const;

export const FEATURE_TREE_LABELS: Record<string, string> = {
  base_cylinder: 'Base Cylinder',
  top_flange_extrusion: 'Top Flange Extrusion',
  bottom_flange_extrusion: 'Bottom Flange Extrusion',
  side_port_boss: 'Side Port Boss',
  upper_bore_cut: 'Upper Bore Cut',
  lower_bore_cut: 'Lower Bore Cut',
  side_port_bore_cut: 'Side Port Bore Cut',
  top_bolt_holes_cut: 'Top Bolt Holes Cut',
  top_counterbores_cut: 'Top Counterbores Cut',
  bottom_bolt_holes_cut: 'Bottom Bolt Holes Cut',
  bottom_counterbores_cut: 'Bottom Counterbores Cut',
  side_port_bolt_holes_cut: 'Side Port Bolt Holes Cut',
  fillets: 'Fillets',
  chamfers: 'Chamfers',
};

// ── API request / response contracts ─────────────────────────────────────────

export interface ExtractRequest {
  // Sent as multipart/form-data; file field name: "blueprint"
}

export interface ExtractResponse {
  params: ExtractedParams;
  source: 'gemini' | 'fallback';
  elapsed_ms: number;
}

export interface GenerateRequest {
  params: LowerValveBodyParams;
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
