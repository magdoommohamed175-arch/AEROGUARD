import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: "application/json",
  },
});

export const getHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};

export const getDatasets = async () => {
  const response = await api.get("/datasets");
  return response.data;
};

export const getFleetSummary = async () => {
  const response = await api.get("/fleet/summary");
  return response.data;
};

export const getFleetTopPriority = async () => {
  const response = await api.get("/fleet/top-priority");
  return response.data;
};

export const getEngine = async (dataset, engineId) => {
  const response = await api.get(
    `/engines/${dataset}/${engineId}`
  );

  return response.data;
};

export const getPrediction = async (dataset, engineId) => {
  const response = await api.get(
    `/prediction/${dataset}/${engineId}`
  );

  return response.data;
};

export const getAnomaly = async (dataset, engineId) => {
  const response = await api.get(
    `/anomaly/${dataset}/${engineId}`
  );

  return response.data;
};

export const getMaintenance = async (dataset, engineId) => {
  const response = await api.get(
    `/maintenance/${dataset}/${engineId}`
  );

  return response.data;
};

export const getExplanation = async (dataset, engineId) => {
  const response = await api.get(
    `/explanation/${dataset}/${engineId}`
  );

  return response.data;
};
export const getTelemetry = async (dataset, engineId) => {
  const response = await api.get(
    `/telemetry/${dataset}/${engineId}`
  );

  return response.data;
};
export const getDegradation = async (dataset, engineId) => {
  const response = await api.get(
    `/degradation/${dataset}/${engineId}`
  );

  return response.data;
};
export const getLiveTelemetry = async (dataset, engineId) => {
  const response = await api.get(
    `/live-telemetry/${dataset}/${engineId}`
  );

  return response.data;
};
export const getFaultInvestigation = async (
  dataset,
  engineId
) => {
  const response = await api.get(
    `/fault-investigation/${dataset}/${engineId}`
  );

  return response.data;
};
export const getEngineComparison = async (
  dataset,
  engine1Id,
  engine2Id
) => {
  const response = await api.get(
    `/compare/${dataset}/${engine1Id}/${engine2Id}`
  );

  return response.data;
};
export default api;