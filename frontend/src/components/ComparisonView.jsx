import React, { useState } from 'react';

/**
 * ComparisonView Component
 * Displays side-by-side comparison of different OCR processing stages
 */
const ComparisonView = ({ result, imageUrl }) => {
  const [leftView, setLeftView] = useState('image');
  const [rightView, setRightView] = useState('cleaned');

  if (!result) {
    return (
      <div className="card p-8 text-center">
        <p className="text-gray-500">No results to compare. Please process an image first.</p>
      </div>
    );
  }

  const viewOptions = [
    { value: 'image', label: 'Original Image', available: !!imageUrl },
    { value: 'raw', label: 'Raw OCR', available: !!result.raw_text },
    { value: 'cleaned', label: 'Cleaned Text', available: !!result.cleaned_text },
    { value: 'transliterated', label: 'Transliterated', available: !!result.transliterated_text },
  ];

  const getViewContent = (viewType) => {
    switch (viewType) {
      case 'image':
        return imageUrl ? (
          <div className="h-full flex items-center justify-center bg-gray-100 rounded">
            <img 
              src={imageUrl} 
              alt="Original document" 
              className="max-h-full max-w-full object-contain"
            />
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-400">
            No image available
          </div>
        );
      
      case 'raw':
        return (
          <div className="h-full overflow-auto p-4 bg-gray-50 rounded">
            <pre className="whitespace-pre-wrap font-mono text-sm">
              {result.raw_text || 'No raw text available'}
            </pre>
          </div>
        );
      
      case 'cleaned':
        return (
          <div className="h-full overflow-auto p-4 bg-green-50 rounded">
            <pre className="whitespace-pre-wrap font-mono text-sm">
              {result.cleaned_text || 'No cleaned text available'}
            </pre>
          </div>
        );
      
      case 'transliterated':
        return (
          <div className="h-full overflow-auto p-4 bg-blue-50 rounded">
            <pre className="whitespace-pre-wrap font-mono text-sm">
              {result.transliterated_text || 'No transliterated text available'}
            </pre>
          </div>
        );
      
      default:
        return <div>Select a view</div>;
    }
  };

  const renderViewSelector = (value, onChange) => (
    <div className="flex flex-wrap gap-2 mb-4">
      {viewOptions.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          disabled={!option.available}
          className={`px-4 py-2 rounded text-sm font-medium transition-colors
            ${value === option.value
              ? 'bg-primary-600 text-white'
              : option.available
              ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );

  const getDiffStats = () => {
    if (!result.raw_text || !result.cleaned_text) return null;

    const rawLength = result.raw_text.length;
    const cleanedLength = result.cleaned_text.length;
    const reduction = ((rawLength - cleanedLength) / rawLength * 100).toFixed(1);

    return (
      <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
        <span>Raw: {rawLength} chars</span>
        <span>→</span>
        <span>Cleaned: {cleanedLength} chars</span>
        <span className="text-primary-600 font-medium">
          ({reduction > 0 ? '-' : '+'}{Math.abs(reduction)}%)
        </span>
      </div>
    );
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Comparison View</h2>
        {getDiffStats()}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold text-gray-700">Left View</h3>
          </div>
          {renderViewSelector(leftView, setLeftView)}
          <div className="border-2 border-gray-300 rounded-lg h-96">
            {getViewContent(leftView)}
          </div>
        </div>

        {/* Right Panel */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold text-gray-700">Right View</h3>
          </div>
          {renderViewSelector(rightView, setRightView)}
          <div className="border-2 border-gray-300 rounded-lg h-96">
            {getViewContent(rightView)}
          </div>
        </div>
      </div>

      {/* Quick Comparison Buttons */}
      <div className="mt-6 flex flex-wrap gap-2">
        <button
          onClick={() => { setLeftView('raw'); setRightView('cleaned'); }}
          className="btn-secondary text-sm"
        >
          Compare Raw vs Cleaned
        </button>
        <button
          onClick={() => { setLeftView('cleaned'); setRightView('transliterated'); }}
          className="btn-secondary text-sm"
        >
          Compare Cleaned vs Transliterated
        </button>
        <button
          onClick={() => { setLeftView('image'); setRightView('cleaned'); }}
          className="btn-secondary text-sm"
        >
          Compare Image vs Text
        </button>
      </div>
    </div>
  );
};

export default ComparisonView;
