import { apiClient } from './client';
import {
  ElGamalDecryptRequest,
  ElGamalDecryptResponse,
  ElGamalDomainGenerateRequest,
  ElGamalDomainGenerateResponse,
  ElGamalEncryptRequest,
  ElGamalEncryptResponse,
  ElGamalKeyGenerateRequest,
  ElGamalKeyGenerateResponse,
  ElGamalPreset,
  HomomorphicMultiplyRequest,
  HomomorphicMultiplyResponse,
  NonceReuseExploitRequest,
  NonceReuseExploitResponse,
} from '../types/elgamal';

export const getElGamalPresets = async (): Promise<ElGamalPreset[]> => {
  const response = await apiClient.get<ElGamalPreset[]>('/elgamal/presets');
  return response.data;
};

export const generateElGamalDomain = async (
  data: ElGamalDomainGenerateRequest
): Promise<ElGamalDomainGenerateResponse> => {
  const response = await apiClient.post<ElGamalDomainGenerateResponse>(
    '/elgamal/generate-domain',
    data
  );
  return response.data;
};

export const generateElGamalKeyPair = async (
  data: ElGamalKeyGenerateRequest
): Promise<ElGamalKeyGenerateResponse> => {
  const response = await apiClient.post<ElGamalKeyGenerateResponse>(
    '/elgamal/generate-keys',
    data
  );
  return response.data;
};

export const encryptElGamal = async (
  data: ElGamalEncryptRequest
): Promise<ElGamalEncryptResponse> => {
  const response = await apiClient.post<ElGamalEncryptResponse>(
    '/elgamal/encrypt',
    data
  );
  return response.data;
};

export const decryptElGamal = async (
  data: ElGamalDecryptRequest
): Promise<ElGamalDecryptResponse> => {
  const response = await apiClient.post<ElGamalDecryptResponse>(
    '/elgamal/decrypt',
    data
  );
  return response.data;
};

export const runHomomorphicMultiply = async (
  data: HomomorphicMultiplyRequest
): Promise<HomomorphicMultiplyResponse> => {
  const response = await apiClient.post<HomomorphicMultiplyResponse>(
    '/elgamal/homomorphic-multiply',
    data
  );
  return response.data;
};

export const exploitNonceReuse = async (
  data: NonceReuseExploitRequest
): Promise<NonceReuseExploitResponse> => {
  const response = await apiClient.post<NonceReuseExploitResponse>(
    '/elgamal/exploit-nonce-reuse',
    data
  );
  return response.data;
};
