import { useEffect, useState } from 'react';

const ProcessingStatus = ({ stages, currentStage, progress = 0 }) => {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(prev => prev + 0.1);
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const allStages = [
    { key: 'preprocessing', label: 'Image Preprocessing', icon: '🖼️' },
    { key: 'ocr', label: 'Text Extraction (OCR)', icon: '📄' },
    { key: 'language_detection', label: 'Language Detection', icon: '🌍' },
    { key: 'cleaning', label: 'Text Cleaning', icon: '✨' },
    { key: 'transliteration', label: 'Transliteration', icon: '🔤' },
  ];

  const getStageStatus = (stageKey) => {
    if (stages && stages[stageKey]) {
      return stages[stageKey].success ? 'completed' : 'failed';
    }
    if (currentStage === stageKey) {
      return 'processing';
    }
    return 'pending';
  };

  const getStageColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'processing':
        return 'text-primary-600 bg-primary-100 animate-pulse';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-400 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return (
          <svg className="h-5 w-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'processing':
        return (
          <svg className="animate-spin h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        );
      case 'failed':
        return (
          <svg className="h-5 w-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <div className="h-5 w-5 rounded-full border-2 border-gray-300"></div>
        );
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Processing Status</h3>
        <span className="text-sm text-gray-500">
          {elapsed.toFixed(1)}s elapsed
        </span>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span className="text-sm font-medium text-gray-700">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-primary-600 h-2.5 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Stages */}
      <div className="space-y-3">
        {allStages.map((stage) => {
          const status = getStageStatus(stage.key);
          const stageData = stages?.[stage.key];

          return (
            <div
              key={stage.key}
              className={`
                flex items-start space-x-3 p-3 rounded-lg transition-all
                ${status === 'processing' ? 'bg-primary-50' : ''}
              `}
            >
              <div className="shrink-0 mt-0.5">
                {getStatusIcon(status)}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <span className="text-xl">{stage.icon}</span>
                  <p className={`
                    text-sm font-medium
                    ${status === 'processing' ? 'text-primary-700' : 'text-gray-700'}
                  `}>
                    {stage.label}
                  </p>
                </div>

                {stageData && (
                  <p className="text-xs text-gray-500 mt-1">
                    Duration: {stageData.duration?.toFixed(2)}s
                  </p>
                )}

                {status === 'processing' && (
                  <p className="text-xs text-primary-600 mt-1 animate-pulse">
                    Processing...
                  </p>
                )}
              </div>

              <div className="shrink-0">
                <span className={`
                  inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                  ${getStageColor(status)}
                `}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProcessingStatus;
