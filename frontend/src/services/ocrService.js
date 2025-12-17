import axios from 'axios';

// API base URL - can be configured via environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for OCR processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', error.response?.data || error.message);
    
    // Handle specific error codes
    if (error.response) {
      switch (error.response.status) {
        case 404:
          throw new Error('Resource not found');
        case 413:
          throw new Error('File too large');
        case 500:
          throw new Error('Server error occurred');
        default:
          throw new Error(error.response.data?.error || 'An error occurred');
      }
    } else if (error.request) {
      throw new Error('No response from server. Please check your connection.');
    } else {
      throw new Error('Request failed: ' + error.message);
    }
  }
);

// OCR Service
const ocrService = {
  /**
   * Upload a file to the server
   * @param {File} file - The file to upload
   * @returns {Promise} - Upload result
   */
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/ocr/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Process an uploaded file through OCR pipeline
   * @param {string} filepath - Server filepath of uploaded file
   * @param {Object} options - Processing options
   * @returns {Promise} - OCR result
   */
  async processFile(filepath, options = {}) {
    const response = await api.post('/api/ocr/process', {
      filepath,
      options: {
        preprocess: options.preprocess !== false,
        use_hybrid_ocr: options.useHybridOCR || false,
        clean_text: options.cleanText !== false,
        transliterate: options.transliterate !== false,
        detect_language: options.detectLanguage !== false,
      },
    });

    return response.data;
  },

  /**
   * Upload and process in one request
   * @param {File} file - The file to upload and process
   * @param {Object} options - Processing options
   * @param {Function} onProgress - Progress callback
   * @returns {Promise} - OCR result
   */
  async uploadAndProcess(file, options = {}, onProgress = null) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('options', JSON.stringify({
      preprocess: options.preprocess !== false,
      use_hybrid_ocr: options.useHybridOCR || false,
      clean_text: options.cleanText !== false,
      transliterate: options.transliterate !== false,
      detect_language: options.detectLanguage !== false,
    }));

    const response = await api.post('/api/ocr/process-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });

    return response.data;
  },

  /**
   * Batch process multiple files
   * @param {File[]} files - Array of files to process
   * @param {Object} options - Processing options
   * @returns {Promise} - Batch result
   */
  async batchProcess(files, options = {}) {
    const formData = new FormData();
    
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    formData.append('options', JSON.stringify({
      preprocess: options.preprocess !== false,
      use_hybrid_ocr: options.useHybridOCR || false,
      clean_text: options.cleanText !== false,
      transliterate: options.transliterate !== false,
      detect_language: options.detectLanguage !== false,
    }));

    const response = await api.post('/api/ocr/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 300000, // 5 minutes for batch
    });

    return response.data;
  },

  /**
   * Get OCR service status
   * @returns {Promise} - Service status
   */
  async getStatus() {
    const response = await api.get('/api/ocr/status');
    return response.data;
  },

  /**
   * Get health status
   * @returns {Promise} - Health status
   */
  async getHealth() {
    const response = await api.get('/api/health');
    return response.data;
  },

  /**
   * Clean up old files
   * @param {number} maxAgeHours - Maximum age of files to keep
   * @returns {Promise} - Cleanup result
   */
  async cleanup(maxAgeHours = 24) {
    const response = await api.post('/api/ocr/cleanup', {
      max_age_hours: maxAgeHours,
    });
    return response.data;
  },
};

export default ocrService;
export { API_BASE_URL };
