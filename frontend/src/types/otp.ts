export interface BitXORTraceSchema {
  bit_index: number;
  bit_m: number;
  bit_k: number;
  bit_c: number;
  equation: string;
}

// Type alias for backwards compatibility
export type BitXORTrace = BitXORTraceSchema;

export interface ByteOTPTraceSchema {
  byte_index: number;
  char_m: string;
  byte_m_val: number;
  byte_m_bin: string;
  byte_k_val: number;
  byte_k_bin: string;
  byte_c_val: number;
  byte_c_bin: string;
  byte_c_hex: string;
  bit_traces: BitXORTraceSchema[];
}

// Type alias for backwards compatibility
export type ByteOTPTrace = ByteOTPTraceSchema;

export interface OTPKeyGenerateRequest {
  length: number;
  format?: 'hex' | 'base64' | 'raw';
}

export interface OTPKeyGenerateResponse {
  key_hex: string;
  key_base64: string;
  length: number;
  entropy: number;
}

export interface OTPEncryptRequest {
  plaintext: string;
  key?: string;
  key_format?: 'hex' | 'ascii';
}

export interface OTPEncryptResponse {
  plaintext_ascii: string;
  key_hex: string;
  key_base64: string;
  ciphertext_hex: string;
  ciphertext_base64: string;
  length: number;
  entropy_plaintext: number;
  entropy_key: number;
  entropy_ciphertext: number;
  byte_traces: ByteOTPTraceSchema[];
  truth_table: string;
}

export interface OTPDecryptRequest {
  ciphertext: string;
  key: string;
  ciphertext_format?: 'hex' | 'base64' | 'ascii';
  key_format?: 'hex' | 'ascii';
}

export interface OTPDecryptResponse {
  recovered_ascii: string;
  recovered_hex: string;
  ciphertext_hex: string;
  key_hex: string;
  length: number;
  is_valid_ascii: boolean;
  byte_traces: ByteOTPTraceSchema[];
}

export interface TwoTimePadAnalyzeRequest {
  c1: string;
  c2: string;
  input_format?: 'hex' | 'base64' | 'ascii';
  p1_known?: string;
}

export interface TwoTimePadAnalyzeResponse {
  c1_hex: string;
  c2_hex: string;
  xor_diff_hex: string;
  length: number;
  proof_steps: string[];
  p1_known_ascii: string | null;
  derived_p2_ascii: string | null;
  shannon_entropy_c1: number;
  shannon_entropy_c2: number;
  shannon_entropy_diff: number;
}

export interface CribDragCandidateSchema {
  position: number;
  crib: string;
  revealed_text: string;
  readability_score: number;
  is_likely_english: boolean;
}

// Type alias for backwards compatibility
export type CribDragCandidate = CribDragCandidateSchema;

export interface CribDragRequest {
  c1: string;
  c2: string;
  input_format?: 'hex' | 'base64' | 'ascii';
  crib: string;
  position?: number;
  min_readability_score?: number;
}

export interface CribDragResponse {
  c1_hex: string;
  c2_hex: string;
  crib: string;
  position: number | null;
  single_result: CribDragCandidateSchema | null;
  candidates: CribDragCandidateSchema[];
  best_candidate: CribDragCandidateSchema | null;
  summary: string;
}

export interface EntropyRequest {
  data: string;
  input_format?: 'text' | 'hex';
}

export interface EntropyResponse {
  entropy: number;
  max_entropy: number;
  efficiency: number;
  length: number;
  unique_symbols: number;
  verdict: string;
  frequency_table: Record<string, number>;
  probability_table: Record<string, number>;
}
