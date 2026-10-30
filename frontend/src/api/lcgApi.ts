import { apiClient } from './client';
import {
  ChiSquareRequest,
  ChiSquareResponse,
  CycleDetectRequest,
  CycleDetectResponse,
  HullDobellRequest,
  HullDobellResponse,
  LCGCrackRequest,
  LCGCrackResponse,
  LCGGenerateRequest,
  LCGGenerateResponse,
  LCGPreset,
  MarsagliaLatticeRequest,
  MarsagliaLatticeResponse,
} from '../types/lcg';

export const getLcgPresets = async (): Promise<LCGPreset[]> => {
  const response = await apiClient.get<LCGPreset[]>('/lcg/presets');
  return response.data;
};

export const generateLcgSequence = async (
  data: LCGGenerateRequest
): Promise<LCGGenerateResponse> => {
  const response = await apiClient.post<LCGGenerateResponse>('/lcg/generate', data);
  return response.data;
};

export const checkHullDobell = async (
  data: HullDobellRequest
): Promise<HullDobellResponse> => {
  const response = await apiClient.post<HullDobellResponse>('/lcg/hull-dobell', data);
  return response.data;
};

export const detectCycle = async (
  data: CycleDetectRequest
): Promise<CycleDetectResponse> => {
  const response = await apiClient.post<CycleDetectResponse>('/lcg/cycle-detect', data);
  return response.data;
};

export const runChiSquare = async (
  data: ChiSquareRequest
): Promise<ChiSquareResponse> => {
  const response = await apiClient.post<ChiSquareResponse>('/lcg/chi-square', data);
  return response.data;
};

export const getMarsagliaLattice = async (
  data: MarsagliaLatticeRequest
): Promise<MarsagliaLatticeResponse> => {
  const response = await apiClient.post<MarsagliaLatticeResponse>(
    '/lcg/marsaglia-lattice',
    data
  );
  return response.data;
};

export const crackLcg = async (
  data: LCGCrackRequest
): Promise<LCGCrackResponse> => {
  const response = await apiClient.post<LCGCrackResponse>('/lcg/crack', data);
  return response.data;
};
