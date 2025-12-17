import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const translationService = {
  /**
   * Translate document from Urdu to English
   */
  translateDocument: async (file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('options', JSON.stringify(options));

    const response = await axios.post(
      `${API_URL}/api/translate/translate-document`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minutes
      }
    );

    return response.data;
  },

  /**
   * Translate plain text
   */
  translateText: async (text, sourceLang = 'ur', targetLang = 'en') => {
    const response = await axios.post(
      `${API_URL}/api/translate/translate-text`,
      {
        text,
        source_lang: sourceLang,
        target_lang: targetLang,
      }
    );

    return response.data;
  },

  /**
   * Generate PDF from translation data
   */
  generatePDF: async (translationData) => {
    const response = await axios.post(
      `${API_URL}/api/translate/generate-pdf`,
      translationData,
      {
        responseType: 'blob',
        timeout: 60000,
      }
    );

    return response.data;
  },

  /**
   * Translate and download PDF in one request
   */
  translateAndDownload: async (file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('options', JSON.stringify(options));

    const response = await axios.post(
      `${API_URL}/api/translate/translate-and-download`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
        timeout: 120000,
      }
    );

    return response.data;
  },

  /**
   * Get translation service status
   */
  getTranslationStatus: async () => {
    const response = await axios.get(`${API_URL}/api/translate/translation-status`);
    return response.data;
  },

  /**
   * Download blob as file
   */
  downloadBlob: (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};

export default translationService;
