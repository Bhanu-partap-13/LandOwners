import { useState } from 'react';

const ResultsDisplay = ({ result, onExport, onReset }) => {
  const [activeTab, setActiveTab] = useState('raw');

  if (!result) {
    return null;
  }

  const tabs = [
    { key: 'raw', label: 'Raw OCR', icon: '📝' },
    { key: 'cleaned', label: 'Cleaned Text', icon: '✨' },
    { key: 'transliterated', label: 'Transliterated', icon: '🔤' },
    { key: 'metadata', label: 'Metadata', icon: '📊' },
  ];

  const getText = () => {
    const resultData = result.data?.result || result.result || {};
    
    switch (activeTab) {
      case 'raw':
        return resultData.raw_text || '';
      case 'cleaned':
        return resultData.cleaned_text || resultData.raw_text || '';
      case 'transliterated':
        return resultData.transliterated_text || resultData.cleaned_text || '';
      default:
        return '';
    }
  };

  const getMetadata = () => {
    const resultData = result.data?.result || result.result || {};
    const processing = result.data?.processing || result.processing || {};
    const language = resultData.language || {};

    return {
      'OCR Confidence': `${resultData.confidence || 0}%`,
      'Primary Language': language.primary_language || language.language || 'Unknown',
      'Language Confidence': `${language.confidence || 0}%`,
      'Processing Time': `${processing.total_time?.toFixed(2) || 0}s`,
      'Word Count': resultData.raw_text?.split(/\s+/).filter(Boolean).length || 0,
      'Character Count': resultData.raw_text?.length || 0,
    };
  };

  const getStagesInfo = () => {
    const processing = result.data?.processing || result.processing || {};
    return processing.stages || {};
  };

  const copyToClipboard = () => {
    const text = getText();
    navigator.clipboard.writeText(text);
    alert('Text copied to clipboard!');
  };

  const downloadText = () => {
    const text = getText();
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ocr_result_${activeTab}_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Success Banner */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center">
          <svg className="h-5 w-5 text-green-600 mr-3" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <div className="flex-1">
            <h3 className="text-sm font-medium text-green-800">
              OCR Processing Completed Successfully
            </h3>
            <p className="text-xs text-green-700 mt-1">
              {result.data?.message || result.message || 'Text extracted and processed'}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-4" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`
                  flex items-center space-x-2 py-4 px-3 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.key
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="mt-6">
          {activeTab === 'metadata' ? (
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900 mb-4">Processing Information</h4>
              
              {/* Metadata Grid */}
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(getMetadata()).map(([key, value]) => (
                  <div key={key} className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 uppercase tracking-wide">{key}</p>
                    <p className="text-lg font-semibold text-gray-900 mt-1">{value}</p>
                  </div>
                ))}
              </div>

              {/* Stages Info */}
              <div className="mt-6">
                <h5 className="font-medium text-gray-900 mb-3">Processing Stages</h5>
                <div className="space-y-2">
                  {Object.entries(getStagesInfo()).map(([stage, data]) => (
                    <div key={stage} className="flex justify-between items-center py-2 border-b border-gray-100">
                      <span className="text-sm text-gray-700 capitalize">{stage.replace('_', ' ')}</span>
                      <span className="text-sm font-medium text-gray-900">
                        {data.duration?.toFixed(2)}s
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Action Buttons */}
              <div className="flex justify-end space-x-2">
                <button
                  onClick={copyToClipboard}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy
                </button>
                
                <button
                  onClick={downloadText}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download
                </button>
              </div>

              {/* Text Display */}
              <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap font-mono text-sm text-gray-800">
                  {getText() || 'No text available'}
                </pre>
              </div>

              {/* Character Count */}
              <p className="text-xs text-gray-500 text-right">
                {getText().length} characters
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-3">
        {onExport && (
          <button
            onClick={() => onExport(result)}
            className="btn-primary flex-1"
          >
            <svg className="h-5 w-5 mr-2 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export Full Result
          </button>
        )}
        
        {onReset && (
          <button
            onClick={onReset}
            className="btn-secondary flex-1"
          >
            <svg className="h-5 w-5 mr-2 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Process Another Document
          </button>
        )}
      </div>
    </div>
  );
};

export default ResultsDisplay;
