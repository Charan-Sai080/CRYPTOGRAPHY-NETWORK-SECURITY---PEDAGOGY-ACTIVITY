export interface LCGPresetSchema {
  name: string;
  description: string;
  m: number;
  a: number;
  c: number;
  default_seed: number;
  is_full_period: boolean;
}

export type LCGPreset = LCGPresetSchema;

export interface LCGStepTraceSchema {
  step: number;
  x_prev: number;
  formula: string;
  product: number;
  product_plus_c: number;
  x_next: number;
  normalized: number;
}

export type LCGStepTrace = LCGStepTraceSchema;

export interface LCGGenerateRequest {
  a?: number;
  c?: number;
  m?: number;
  seed?: number;
  count?: number;
  preset_name?: string;
}

export interface LCGGenerateResponse {
  parameters: Record<string, number>;
  values: number[];
  normalized: number[];
  traces: LCGStepTraceSchema[];
}

export interface HullDobellConditionSchema {
  satisfied: boolean;
  description: string;
  detail: string;
}

export type HullDobellCondition = HullDobellConditionSchema;

export interface HullDobellRequest {
  a?: number;
  c?: number;
  m?: number;
  preset_name?: string;
}

export interface HullDobellResponse {
  a: number;
  c: number;
  m: number;
  is_full_period: boolean;
  condition_1: HullDobellConditionSchema;
  condition_2: HullDobellConditionSchema;
  condition_3: HullDobellConditionSchema;
  prime_factors_m: number[];
  explanation: string;
}

export interface FloydStepTraceSchema {
  step: number;
  tortoise: number;
  hare: number;
}

export type FloydStepTrace = FloydStepTraceSchema;

export interface CycleDetectRequest {
  a?: number;
  c?: number;
  m?: number;
  seed?: number;
  max_steps?: number;
  preset_name?: string;
}

export interface CycleDetectResponse {
  period: number;
  cycle_start: number;
  total_steps: number;
  is_full_period: boolean;
  sample_cycle: number[];
  traces: FloydStepTraceSchema[];
}

export interface ChiSquareBinSchema {
  bin_index: number;
  range_start: number;
  range_end: number;
  observed_count: number;
  expected_count: number;
  deviation: number;
}

export type ChiSquareBin = ChiSquareBinSchema;

export interface ChiSquareRequest {
  a?: number;
  c?: number;
  m?: number;
  seed?: number;
  count: number;
  num_bins: number;
  preset_name?: string;
  sequence?: number[];
}

export interface ChiSquareResponse {
  chi_square_stat: number;
  degrees_of_freedom: number;
  critical_value: number;
  p_value_approx: number;
  is_uniform: boolean;
  bins: ChiSquareBinSchema[];
  explanation: string;
}

export interface LatticePoint2DSchema {
  x: number;
  y: number;
}

export type LatticePoint2D = LatticePoint2DSchema;

export interface LatticePoint3DSchema {
  x: number;
  y: number;
  z: number;
}

export type LatticePoint3D = LatticePoint3DSchema;

export interface MarsagliaLatticeRequest {
  a?: number;
  c?: number;
  m?: number;
  seed?: number;
  count?: number;
  dimension: 2 | 3;
  preset_name?: string;
}

export interface MarsagliaLatticeResponse {
  dimension: number;
  count: number;
  theoretical_max_hyperplanes: number;
  points_2d: LatticePoint2DSchema[];
  points_3d: LatticePoint3DSchema[];
  explanation: string;
}

export interface LCGCrackRequest {
  outputs: number[];
  m: number;
}

export interface LCGCrackResponse {
  is_successful: boolean;
  m: number;
  recovered_a: number | null;
  recovered_c: number | null;
  predicted_next: number | null;
  steps: string[];
  notes: string;
}
