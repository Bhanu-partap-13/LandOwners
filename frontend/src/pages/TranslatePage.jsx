import React, { useState } from 'react';
import translationService from '../services/translationService';

const TranslatePage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [translationResult, setTranslationResult] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
      setError('Please select a valid image (JPG, PNG) or PDF file');
      return;
    }

    // Validate file size (16MB)
    if (file.size > 16 * 1024 * 1024) {
      setError('File size must be less than 16MB');
      return;
    }

    setSelectedFile(file);
    setError(null);
    setTranslationResult(null);

    // Create preview for images
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    } else {
      setPreview(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      const fakeEvent = { target: { files: [file] } };
      handleFileSelect(fakeEvent);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleTranslate = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      const response = await translationService.translateDocument(selectedFile, {
        preprocess: true,
        clean_text: true,
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (response.success) {
        setTranslationResult(response.data);
      } else {
        setError(response.error || 'Translation failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Translation failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!translationResult) return;

    try {
      setIsProcessing(true);
      const pdfBlob = await translationService.generatePDF(translationResult);
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const filename = `jamabandi_translation_${timestamp}.pdf`;
      
      translationService.downloadBlob(pdfBlob, filename);
    } catch (err) {
      setError('Failed to generate PDF: ' + (err.message || 'Unknown error'));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTranslateAndDownload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const pdfBlob = await translationService.translateAndDownload(selectedFile, {
        preprocess: true,
        clean_text: true,
      });

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const filename = `jamabandi_translation_${timestamp}.pdf`;
      
      translationService.downloadBlob(pdfBlob, filename);
      
      // Also run translation to show results
      await handleTranslate();
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Translation failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setTranslationResult(null);
    setError(null);
    setProgress(0);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📄 Land Record Translation
          </h1>
          <p className="text-lg text-gray-600">
            Translate Urdu Jamabandi documents to English with precise accuracy
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Using Setu-Translate for authentic translation of land ownership records
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <span className="text-red-600 mr-2">⚠️</span>
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Section */}
          <div className="card">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Upload Document</h2>
            
            {/* Drop Zone */}
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                selectedFile
                  ? 'border-green-400 bg-green-50'
                  : 'border-gray-300 bg-gray-50 hover:border-primary-400'
              }`}
            >
              {preview ? (
                <div className="space-y-4">
                  <img
                    src={preview}
                    alt="Preview"
                    className="max-h-64 mx-auto rounded-lg shadow-md"
                  />
                  <p className="text-sm text-gray-600">{selectedFile.name}</p>
                </div>
              ) : selectedFile ? (
                <div className="space-y-2">
                  <div className="text-5xl">📄</div>
                  <p className="font-medium text-gray-700">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="text-6xl">📤</div>
                  <div>
                    <label className="btn-primary cursor-pointer">
                      Choose File
                      <input
                        type="file"
                        accept="image/jpeg,image/jpg,image/png,application/pdf"
                        onChange={handleFileSelect}
                        className="hidden"
                      />
                    </label>
                  </div>
                  <p className="text-sm text-gray-500">
                    or drag and drop your Jamabandi document here
                  </p>
                  <p className="text-xs text-gray-400">
                    Supports: JPG, PNG, PDF (max 16MB)
                  </p>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            {selectedFile && (
              <div className="mt-6 space-y-3">
                <button
                  onClick={handleTranslate}
                  disabled={isProcessing}
                  className="w-full btn-primary"
                >
                  {isProcessing ? '⏳ Translating...' : '🔄 Translate Document'}
                </button>
                
                <button
                  onClick={handleTranslateAndDownload}
                  disabled={isProcessing}
                  className="w-full bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {isProcessing ? '⏳ Processing...' : '⚡ Translate & Download PDF'}
                </button>

                <button
                  onClick={handleReset}
                  disabled={isProcessing}
                  className="w-full btn-secondary"
                >
                  🔄 Reset
                </button>
              </div>
            )}

            {/* Progress Bar */}
            {isProcessing && (
              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 text-center mt-2">
                  Processing... {progress}%
                </p>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="card">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Translation Result</h2>

            {translationResult ? (
              <div className="space-y-6">
                {/* Metadata */}
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">Translation Info</h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-blue-700">Source:</span>
                      <span className="ml-2 font-medium">
                        {translationResult.metadata.source_language.toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <span className="text-blue-700">Target:</span>
                      <span className="ml-2 font-medium">
                        {translationResult.metadata.target_language.toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <span className="text-blue-700">Confidence:</span>
                      <span className="ml-2 font-medium">
                        {(translationResult.metadata.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-blue-700">Method:</span>
                      <span className="ml-2 font-medium">
                        {translationResult.metadata.method}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Original Text */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2 flex items-center">
                    📜 Original Text (Urdu)
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-4 max-h-48 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 font-arabic">
                      {translationResult.original.cleaned_text}
                    </pre>
                  </div>
                </div>

                {/* Translated Text */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2 flex items-center">
                    ✅ Translated Text (English)
                  </h3>
                  <div className="bg-green-50 rounded-lg p-4 max-h-48 overflow-y-auto border-2 border-green-200">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800">
                      {translationResult.translated.text}
                    </pre>
                  </div>
                </div>

                {/* Download Button */}
                <button
                  onClick={handleDownloadPDF}
                  disabled={isProcessing}
                  className="w-full bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 font-medium flex items-center justify-center gap-2"
                >
                  <span>📥</span>
                  <span>Download as PDF</span>
                </button>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <div className="text-6xl mb-4">📄</div>
                <p className="text-lg">Upload and translate a document to see results</p>
                <p className="text-sm mt-2">
                  Your translated text will appear here
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-8 card bg-blue-50 border border-blue-200">
          <h3 className="text-lg font-bold text-blue-900 mb-3">
            📋 About Jamabandi Translation
          </h3>
          <div className="space-y-2 text-sm text-blue-800">
            <p>
              <strong>Jamabandi (جمع بندی)</strong> is a land ownership and cultivation record
              used in Jammu & Kashmir and other regions of India.
            </p>
            <p>
              This tool uses advanced OCR and Setu-Translate to accurately convert Urdu land
              records into English, preserving the document structure and terminology.
            </p>
            <p>
              <strong>Common Terms:</strong>
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>موضع (Mauza) = Village</li>
              <li>تحصیل (Tehsil) = Tehsil/Sub-district</li>
              <li>ضلع (Zila) = District</li>
              <li>خسرہ (Khasra) = Survey Number</li>
              <li>مالک (Malik) = Owner</li>
              <li>رقبہ (Raqba) = Area</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TranslatePage;
