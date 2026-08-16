import type { LowerValveBodyParams, ParamFieldStatus } from '@vexform/types'

export const LOWER_VALVE_BODY_REFERENCE: LowerValveBodyParams = {
  overall_height: 118,
  outer_body_diameter: 36,
  main_bore_upper_diameter: 28,
  main_bore_lower_inner_diameter: 26,
  main_bore_lower_outer_step_diameter: 28,
  side_port_bore_diameter: 20,
  top_flange_outer_diameter: 40,
  top_flange_bolt_hole_diameter: 7,
  top_flange_bolt_hole_depth: 6,
  top_flange_bolt_hole_count: 4,
  top_flange_counterbore_diameter: 13,
  top_flange_counterbore_depth: 1,
  bottom_flange_outer_diameter: 36,
  bottom_flange_bolt_circle_diameter: 52,
  bottom_flange_outer_flange_diameter: 65,
  bottom_flange_bolt_hole_diameter: 7,
  bottom_flange_bolt_hole_count: 4,
  bottom_flange_counterbore_diameter: 13,
  bottom_flange_counterbore_depth: 1,
  side_port_flange_outer_diameter: 34,
  side_port_bolt_hole_diameter: 7,
  side_port_bolt_hole_spacing: 52,
  side_port_angle_degrees: 135,
  side_port_offset_from_top: 58,
  unspecified_fillet_radius: 1,
  internal_step_chamfer: 1.5,
  other_chamfer: 1,
  material: 'HT150',
}

export const PARAM_LABELS: Record<keyof LowerValveBodyParams, string> = {
  overall_height: 'Overall Height',
  outer_body_diameter: 'Outer Body Diameter',
  main_bore_upper_diameter: 'Main Bore Upper Ø',
  main_bore_lower_inner_diameter: 'Main Bore Lower Inner Ø',
  main_bore_lower_outer_step_diameter: 'Main Bore Lower Outer Step Ø',
  side_port_bore_diameter: 'Side Port Bore Ø',
  top_flange_outer_diameter: 'Top Flange Outer Ø',
  top_flange_bolt_hole_diameter: 'Top Flange Bolt Hole Ø',
  top_flange_bolt_hole_depth: 'Top Flange Bolt Hole Depth',
  top_flange_bolt_hole_count: 'Top Flange Bolt Hole Count',
  top_flange_counterbore_diameter: 'Top Flange Counterbore Ø',
  top_flange_counterbore_depth: 'Top Flange Counterbore Depth',
  bottom_flange_outer_diameter: 'Bottom Flange Outer Ø (body)',
  bottom_flange_bolt_circle_diameter: 'Bottom Flange Bolt Circle Ø',
  bottom_flange_outer_flange_diameter: 'Bottom Flange Overall Ø',
  bottom_flange_bolt_hole_diameter: 'Bottom Flange Bolt Hole Ø',
  bottom_flange_bolt_hole_count: 'Bottom Flange Bolt Hole Count',
  bottom_flange_counterbore_diameter: 'Bottom Flange Counterbore Ø',
  bottom_flange_counterbore_depth: 'Bottom Flange Counterbore Depth',
  side_port_flange_outer_diameter: 'Side Port Flange Outer Ø',
  side_port_bolt_hole_diameter: 'Side Port Bolt Hole Ø',
  side_port_bolt_hole_spacing: 'Side Port Bolt Hole Spacing',
  side_port_angle_degrees: 'Side Port Angle',
  side_port_offset_from_top: 'Side Port Offset from Top',
  unspecified_fillet_radius: 'Unspecified Fillet Radius',
  internal_step_chamfer: 'Internal Step Chamfer',
  other_chamfer: 'Other Chamfer',
  material: 'Material',
}

export const PARAM_UNITS: Partial<Record<keyof LowerValveBodyParams, string>> = {
  overall_height: 'mm',
  outer_body_diameter: 'mm',
  main_bore_upper_diameter: 'mm',
  main_bore_lower_inner_diameter: 'mm',
  main_bore_lower_outer_step_diameter: 'mm',
  side_port_bore_diameter: 'mm',
  top_flange_outer_diameter: 'mm',
  top_flange_bolt_hole_diameter: 'mm',
  top_flange_bolt_hole_depth: 'mm',
  top_flange_counterbore_diameter: 'mm',
  top_flange_counterbore_depth: 'mm',
  bottom_flange_outer_diameter: 'mm',
  bottom_flange_bolt_circle_diameter: 'mm',
  bottom_flange_outer_flange_diameter: 'mm',
  bottom_flange_bolt_hole_diameter: 'mm',
  bottom_flange_counterbore_diameter: 'mm',
  bottom_flange_counterbore_depth: 'mm',
  side_port_flange_outer_diameter: 'mm',
  side_port_bolt_hole_diameter: 'mm',
  side_port_bolt_hole_spacing: 'mm',
  side_port_angle_degrees: '°',
  side_port_offset_from_top: 'mm',
  unspecified_fillet_radius: 'mm',
  internal_step_chamfer: 'mm',
  other_chamfer: 'mm',
}

const ACCEPTED_MIMES = new Set(['image/jpeg', 'image/png', 'application/pdf'])
const MAX_BYTES = 20 * 1024 * 1024

export function validateBlueprint(mimeType: string, sizeBytes: number): { valid: boolean; error?: string } {
  if (!ACCEPTED_MIMES.has(mimeType)) {
    return { valid: false, error: 'Invalid file type. Accepted formats: JPEG, PNG, PDF.' }
  }
  if (sizeBytes > MAX_BYTES) {
    return { valid: false, error: 'File exceeds the 20 MB size limit.' }
  }
  return { valid: true }
}

export function computeFieldStatus(
  extracted: number,
  reference: number
): ParamFieldStatus {
  if (reference === 0) return 'ai_match'
  const deviation = Math.abs(extracted - reference) / Math.abs(reference)
  return deviation > 0.2 ? 'ai_deviation' : 'ai_match'
}

export const PARAM_SECTIONS: Array<{
  label: string
  keys: Array<keyof LowerValveBodyParams>
}> = [
  {
    label: 'Main Body',
    keys: ['overall_height', 'outer_body_diameter', 'material'],
  },
  {
    label: 'Main Bore',
    keys: [
      'main_bore_upper_diameter',
      'main_bore_lower_inner_diameter',
      'main_bore_lower_outer_step_diameter',
    ],
  },
  {
    label: 'Top Flange',
    keys: [
      'top_flange_outer_diameter',
      'top_flange_bolt_hole_diameter',
      'top_flange_bolt_hole_depth',
      'top_flange_bolt_hole_count',
      'top_flange_counterbore_diameter',
      'top_flange_counterbore_depth',
    ],
  },
  {
    label: 'Bottom Flange',
    keys: [
      'bottom_flange_outer_diameter',
      'bottom_flange_bolt_circle_diameter',
      'bottom_flange_outer_flange_diameter',
      'bottom_flange_bolt_hole_diameter',
      'bottom_flange_bolt_hole_count',
      'bottom_flange_counterbore_diameter',
      'bottom_flange_counterbore_depth',
    ],
  },
  {
    label: 'Side Port',
    keys: [
      'side_port_bore_diameter',
      'side_port_flange_outer_diameter',
      'side_port_bolt_hole_diameter',
      'side_port_bolt_hole_spacing',
      'side_port_angle_degrees',
      'side_port_offset_from_top',
    ],
  },
  {
    label: 'Fillets & Chamfers',
    keys: ['unspecified_fillet_radius', 'internal_step_chamfer', 'other_chamfer'],
  },
]
