import { apiClient } from './client';
import {
  CribDragRequest,
  CribDragResponse,
  EntropyRequest,
  EntropyResponse,
  OTPDecryptRequest,
  OTPDecryptResponse,
  OTPEncryptRequest,
  OTPEncryptResponse,
  OTPKeyGenerateRequest,
  OTPKeyGenerateResponse,
  TwoTimePadAnalyzeRequest,
  TwoTimePadAnalyzeResponse,
} from '../types/otp';

export const generateOtpKey = async (
  data: OTPKeyGenerateRequest
): Promise<OTPKeyGenerateResponse> => {
  const response = await apiClient.post<OTPKeyGenerateResponse>(
    '/otp/generate-key',
    data
  );
  return response.data;
};

export const encryptOtp = async (
  data: OTPEncryptRequest
): Promise<OTPEncryptResponse> => {
  const response = await apiClient.post<OTPEncryptResponse>('/otp/encrypt', data);
  return response.data;
};

export const decryptOtp = async (
  data: OTPDecryptRequest
): Promise<OTPDecryptResponse> => {
  const response = await apiClient.post<OTPDecryptResponse>('/otp/decrypt', data);
  return response.data;
};

export const analyzeTwoTimePad = async (
  data: TwoTimePadAnalyzeRequest
): Promise<TwoTimePadAnalyzeResponse> => {
  const response = await apiClient.post<TwoTimePadAnalyzeResponse>(
    '/otp/two-time-pad/analyze',
    data
  );
  return response.data;
};

export const runCribDrag = async (
  data: CribDragRequest
): Promise<CribDragResponse> => {
  const response = await apiClient.post<CribDragResponse>(
    '/otp/two-time-pad/crib-drag',
    data
  );
  return response.data;
};

export const calculateEntropy = async (
  data: EntropyRequest
): Promise<EntropyResponse> => {
  const response = await apiClient.post<EntropyResponse>('/otp/entropy', data);
  return response.data;
};
