import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const videoAPI = {
  // Upload video
  uploadVideo: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(progress);
        }
      },
    });

    return response.data;
  },

  // Get video status
  getVideoStatus: async (videoId) => {
    const response = await api.get(`/videos/${videoId}/status`);
    return response.data;
  },

  // Trigger analysis
  triggerAnalysis: async (videoId) => {
    const response = await api.post(`/videos/${videoId}/analyze`);
    return response.data;
  },

  // Get analysis results
  getAnalysis: async (videoId) => {
    const response = await api.get(`/videos/${videoId}/analysis`);
    return response.data;
  },

  // Update metadata (headline/location)
  updateMetadata: async (videoId, metadata) => {
    const response = await api.patch(`/videos/${videoId}/metadata`, metadata);
    return response.data;
  },

  // Trigger rendering
  triggerRender: async (videoId, renderSettings) => {
    const response = await api.post(`/videos/${videoId}/render`, renderSettings);
    return response.data;
  },

  // Get output info
  getOutput: async (videoId) => {
    const response = await api.get(`/videos/${videoId}/output`);
    return response.data;
  },

  // Get download URL
  getDownloadURL: (videoId) => {
    return `${API_BASE_URL}/videos/${videoId}/download`;
  },
};

export default api;
