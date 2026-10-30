export interface ElGamalPresetSchema {
  name: string;
  description: string;
  p: number | string;
  g: number | string;
  p_bits: number;
  is_safe_prime: boolean;
}

export type ElGamalPreset = ElGamalPresetSchema;

export interface ElGamalDomainGenerateRequest {
  bits?: number;
}

export interface ElGamalDomainGenerateResponse {
  p: number;
  g: number;
  p_str: string;
  g_str: string;
  p_bits: number;
  steps: string[];
}

export interface ElGamalPublicKeySchema {
  p: number;
  g: number;
  y: number;
  p_str: string;
  g_str: string;
  y_str: string;
}

export type ElGamalPublicKey = ElGamalPublicKeySchema;

export interface ElGamalPrivateKeySchema {
  p: number;
  g: number;
  x: number;
  p_str: string;
  g_str: string;
  x_str: string;
}

export type ElGamalPrivateKey = ElGamalPrivateKeySchema;

export interface ElGamalKeyGenerateRequest {
  p?: number;
  g?: number;
  preset_name?: string;
  seed_x?: number;
}

export interface ElGamalKeyGenerateResponse {
  public_key: ElGamalPublicKeySchema;
  private_key: ElGamalPrivateKeySchema;
}

export interface ElGamalCiphertextBlockSchema {
  index: number;
  c1: number;
  c2: number;
  c1_str: string;
  c2_str: string;
  original_length: number;
}

export type ElGamalCiphertextBlock = ElGamalCiphertextBlockSchema;

export interface ElGamalEncryptTraceSchema {
  m: number;
  k: number;
  y: number;
  p: number;
  g: number;
  c1: number;
  c2: number;
  shared_secret_s: number;
  formula_c1: string;
  formula_s: string;
  formula_c2: string;
}

export type ElGamalEncryptTrace = ElGamalEncryptTraceSchema;

export interface ElGamalEncryptRequest {
  p: number;
  g: number;
  y: number;
  message_int?: number;
  message_text?: string;
  seed_k?: number;
}

export interface ElGamalEncryptResponse {
  is_multi_block: boolean;
  c1: number | null;
  c2: number | null;
  c1_str: string | null;
  c2_str: string | null;
  blocks: ElGamalCiphertextBlockSchema[];
  single_trace: ElGamalEncryptTraceSchema | null;
  block_traces: ElGamalEncryptTraceSchema[];
  block_size_bytes: number;
}

export interface ElGamalDecryptTraceSchema {
  c1: number;
  c2: number;
  x: number;
  p: number;
  shared_secret_s: number;
  s_inv: number;
  recovered_m: number;
  formula_s: string;
  formula_s_inv: string;
  formula_m: string;
}

export type ElGamalDecryptTrace = ElGamalDecryptTraceSchema;

export interface ElGamalDecryptRequest {
  p: number;
  x: number;
  c1?: number;
  c2?: number;
  blocks?: ElGamalCiphertextBlockSchema[];
}

export interface ElGamalDecryptResponse {
  is_multi_block: boolean;
  recovered_int: number | null;
  recovered_text: string | null;
  single_trace: ElGamalDecryptTraceSchema | null;
  block_traces: ElGamalDecryptTraceSchema[];
}

export interface HomomorphicMultiplyRequest {
  m1: number;
  m2: number;
  p: number;
  g: number;
  y: number;
  x?: number;
  seed_k1?: number;
  seed_k2?: number;
}

export interface HomomorphicMultiplyResponse {
  m1: number;
  m2: number;
  p: number;
  c1_a: number;
  c2_a: number;
  c1_b: number;
  c2_b: number;
  c1_mult: number;
  c2_mult: number;
  expected_product: number;
  decrypted_product: number | null;
  is_verified: boolean;
  explanation: string;
}

export interface NonceReuseExploitRequest {
  p: number;
  c1_a: number;
  c2_a: number;
  c1_b: number;
  c2_b: number;
  m1_known: number;
}

export interface NonceReuseExploitResponse {
  is_attack_applicable: boolean;
  p: number;
  c1_identical: boolean;
  m1_known: number;
  recovered_m2: number | null;
  ratio: number | null;
  proof_steps: string[];
  explanation: string;
  formula?: string;
  notes?: string;
}
