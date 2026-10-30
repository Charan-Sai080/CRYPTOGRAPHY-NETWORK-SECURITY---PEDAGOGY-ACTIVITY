import { apiClient } from './client';
import {
  DSADomainGenerateRequest,
  DSADomainGenerateResponse,
  DSAKeyGenerateRequest,
  DSAKeyGenerateResponse,
  DSANonceReuseExploitRequest,
  DSANonceReuseExploitResponse,
  DSAPreset,
  DSASignRequest,
  DSASignResponse,
  DSATamperRequest,
  DSATamperResponse,
  DSAVerifyRequest,
  DSAVerifyResponse,
} from '../types/dsa';

export const getDsaPresets = async (): Promise<DSAPreset[]> => {
  const response = await apiClient.get<DSAPreset[]>('/dsa/presets');
  return response.data;
};

export const generateDsaDomain = async (
  data: DSADomainGenerateRequest
): Promise<DSADomainGenerateResponse> => {
  const response = await apiClient.post<DSADomainGenerateResponse>(
    '/dsa/generate-domain',
    data
  );
  return response.data;
};

export const generateDsaKeyPair = async (
  data: DSAKeyGenerateRequest
): Promise<DSAKeyGenerateResponse> => {
  const response = await apiClient.post<DSAKeyGenerateResponse>(
    '/dsa/generate-keys',
    data
  );
  return response.data;
};

export const signDsaMessage = async (
  data: DSASignRequest
): Promise<DSASignResponse> => {
  const response = await apiClient.post<DSASignResponse>('/dsa/sign', data);
  return response.data;
};

export const verifyDsaSignature = async (
  data: DSAVerifyRequest
): Promise<DSAVerifyResponse> => {
  const response = await apiClient.post<DSAVerifyResponse>('/dsa/verify', data);
  return response.data;
};

export const detectTampering = async (
  data: DSATamperRequest
): Promise<DSATamperResponse> => {
  const response = await apiClient.post<DSATamperResponse>(
    '/dsa/detect-tampering',
    data
  );
  return response.data;
};

export const exploitDsaNonceReuse = async (
  data: DSANonceReuseExploitRequest
): Promise<DSANonceReuseExploitResponse> => {
  const response = await apiClient.post<DSANonceReuseExploitResponse>(
    '/dsa/exploit-nonce-reuse',
    data
  );
  return response.data;
};
