export interface DSAPresetSchema {
  name: string;
  p: number | string;
  q: number | string;
  g: number | string;
  p_str: string;
  q_str: string;
  g_str: string;
  p_bits: number;
  q_bits: number;
}

export type DSAPreset = DSAPresetSchema;

export interface DSADomainGenerateRequest {
  p_bits?: number;
  q_bits?: number;
}

export interface DSADomainGenerateResponse {
  p: number;
  q: number;
  g: number;
  p_str: string;
  q_str: string;
  g_str: string;
  p_bits: number;
  q_bits: number;
  logs: string[];
  steps?: string[];
}

export interface DSAPublicKeySchema {
  p: number;
  q: number;
  g: number;
  y: number;
  p_str: string;
  q_str: string;
  g_str: string;
  y_str: string;
}

export type DSAPublicKey = DSAPublicKeySchema;

export interface DSAPrivateKeySchema {
  p: number;
  q: number;
  g: number;
  x: number;
  p_str: string;
  q_str: string;
  g_str: string;
  x_str: string;
}

export type DSAPrivateKey = DSAPrivateKeySchema;

export interface DSAKeyGenerateRequest {
  p?: number;
  q?: number;
  g?: number;
  preset_name?: string;
  seed_x?: number;
}

export interface DSAKeyGenerateResponse {
  public_key: DSAPublicKeySchema;
  private_key: DSAPrivateKeySchema;
}

export interface DSASignTraceSchema {
  message: string;
  hash_hex: string;
  hash_int: number;
  k: number;
  r: number;
  s: number;
  k_inv: number;
  p: number;
  q: number;
  g: number;
  x: number;
  formula_r: string;
  formula_s: string;
  resample_count: number;
}

export type DSASignTrace = DSASignTraceSchema;

export interface DSASignRequest {
  message: string;
  p: number;
  q: number;
  g: number;
  x: number;
  seed_k?: number;
}

export interface DSASignResponse {
  r: number;
  s: number;
  r_str: string;
  s_str: string;
  hash_hex: string;
  hash_int: number;
  trace: DSASignTraceSchema;
}

export interface DSAVerifyTraceSchema {
  message: string;
  hash_int: number;
  r: number;
  s: number;
  w: number;
  u1: number;
  u2: number;
  v: number;
  is_valid: boolean;
  p: number;
  q: number;
  g: number;
  y: number;
  formula_w: string;
  formula_u1: string;
  formula_u2: string;
  formula_v: string;
}

export type DSAVerifyTrace = DSAVerifyTraceSchema;

export interface DSAVerifyRequest {
  message: string;
  r: number;
  s: number;
  p: number;
  q: number;
  g: number;
  y: number;
}

export interface DSAVerifyResponse {
  is_valid: boolean;
  reason: string;
  v: number | null;
  r: number;
  trace: DSAVerifyTraceSchema | null;
}

export interface DSATamperRequest {
  message: string;
  p: number;
  q: number;
  g: number;
  x: number;
  y: number;
  tamper_target: 'message' | 'r' | 's';
  bit_index: number;
  seed_k?: number;
}

export interface DSATamperResponse {
  tamper_detected: boolean;
  tamper_type: string;
  bit_flipped: number;
  original_message: string;
  tampered_message: string;
  original_signature: { r: number; s: number };
  tampered_signature: { r: number; s: number };
  original_verification: boolean;
  tampered_verification: boolean;
}

export interface DSANonceReuseExploitRequest {
  m1: string;
  r1: number;
  s1: number;
  m2: string;
  r2: number;
  s2: number;
  p: number;
  q: number;
  g: number;
  y: number;
}

export interface DSANonceReuseExploitResponse {
  is_exploit_applicable: boolean;
  recovered_k: number | null;
  recovered_x: number | null;
  recovered_k_str: string | null;
  recovered_x_str: string | null;
  is_valid_private_key: boolean;
  public_key_matched: boolean;
  steps: string[];
  proof_summary: string;
  historical_context: string;
}
