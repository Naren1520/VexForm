import type { FieldDef, ShapeSchema, ShapeParams, ParamFieldStatus } from '@vexform/types'

// ── Field status helpers ───────────────────────────────────────────────────────

export function computeFieldStatus(
  extracted: number,
  reference: number
): ParamFieldStatus {
  if (reference === 0) return 'ai_match'
  const deviation = Math.abs(extracted - reference) / Math.abs(reference)
  return deviation > 0.2 ? 'ai_deviation' : 'ai_match'
}

// ── Blueprint file validation ─────────────────────────────────────────────────

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

// ── Dynamic field helpers from schema ─────────────────────────────────────────

export function getFieldDef(schema: ShapeSchema, key: string): FieldDef | undefined {
  return schema.fields.find((f) => f.key === key)
}

export function getFieldLabel(schema: ShapeSchema, key: string): string {
  return schema.fields.find((f) => f.key === key)?.label ?? key
}

export function getFieldUnit(schema: ShapeSchema, key: string): string {
  return schema.fields.find((f) => f.key === key)?.unit ?? ''
}

export function isIntField(schema: ShapeSchema, key: string): boolean {
  return schema.fields.find((f) => f.key === key)?.field_type === 'int'
}

export function isStringField(schema: ShapeSchema, key: string): boolean {
  return schema.fields.find((f) => f.key === key)?.field_type === 'string'
}

/** Build params dict suitable for /generate from the current form state.
 *  For generic shapes, the CAD-IR is passed through as-is.
 *  For all other shapes, values are coerced to their correct types.
 */
export function buildParamsFromFormState(
  schema: ShapeSchema,
  formState: Record<string, { value: number | string; status: string }>,
  extractedParams?: Record<string, any>
): ShapeParams {
  const params: ShapeParams = {}

  // Preserve AI-generated geometry alongside editable form values.
  if (schema.shape_type === 'programmatic' && extractedParams?.['construction_program']) {
    params['construction_program'] = extractedParams['construction_program']
  }
  if ((schema.shape_type === 'programmatic' || schema.shape_type === 'cad_ir') && extractedParams?.['cad_ir']) {
    params['cad_ir'] = extractedParams['cad_ir']
  }

  for (const field of schema.fields) {
    const fieldState = formState[field.key]
    const raw = fieldState !== undefined
      ? fieldState.value
      : (schema.reference_values[field.key] ?? null)

    if (field.field_type === 'string') {
      params[field.key] = raw !== null && raw !== undefined ? String(raw) : ''
    } else if (field.field_type === 'int') {
      const n = typeof raw === 'number' ? raw : parseInt(String(raw), 10)
      params[field.key] = Number.isFinite(n) ? n : (schema.reference_values[field.key] as number ?? 1)
    } else {
      // float
      const n = typeof raw === 'number' ? raw : parseFloat(String(raw))
      params[field.key] = Number.isFinite(n) ? n : (schema.reference_values[field.key] as number ?? 0)
    }
  }

  return params
}

// ── Legacy Lower Valve Body constants (for backwards compatibility) ─────────
// These are still used in any file that hasn't been updated to use the dynamic schema.

export const LOWER_VALVE_BODY_REFERENCE: ShapeParams = {
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
