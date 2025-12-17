import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ImageUpload from '../src/components/ImageUpload';
import ProcessingStatus from '../src/components/ProcessingStatus';
import ResultsDisplay from '../src/components/ResultsDisplay';
import ComparisonView from '../src/components/ComparisonView';

// Mock data
const mockResult = {
  raw_text: 'Sample raw text from OCR',
  cleaned_text: 'Sample cleaned text',
  transliterated_text: 'Sample transliterated text',
  language: {
    detected: 'en',
    confidence: 0.95
  },
  metadata: {
    ocr_confidence: 0.88,
    word_count: 5,
    character_count: 25
  },
  processing: {
    total_time: 2.5,
    stages: {
      preprocessing: { duration: 0.5 },
      ocr: { duration: 1.2 },
      language_detection: { duration: 0.3 },
      cleaning: { duration: 0.3 },
      transliteration: { duration: 0.2 }
    }
  }
};

const mockStages = {
  preprocessing: { duration: 0.5, status: 'completed' },
  ocr: { duration: 1.2, status: 'completed' },
  language_detection: { duration: 0.3, status: 'completed' },
  cleaning: { duration: 0.3, status: 'completed' },
  transliteration: { duration: 0.2, status: 'completed' }
};

// ImageUpload Component Tests
describe('ImageUpload Component', () => {
  const mockOnUpload = vi.fn();

  beforeEach(() => {
    mockOnUpload.mockClear();
  });

  it('renders upload component', () => {
    render(<ImageUpload onUpload={mockOnUpload} isProcessing={false} />);
    expect(screen.getByText(/Upload Land Record Image/i)).toBeInTheDocument();
  });

  it('handles file selection', async () => {
    render(<ImageUpload onUpload={mockOnUpload} isProcessing={false} />);
    
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const input = screen.getByLabelText(/click to select/i);
    
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText(/test.jpg/i)).toBeInTheDocument();
    });
  });

  it('validates file type', async () => {
    render(<ImageUpload onUpload={mockOnUpload} isProcessing={false} />);
    
    const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByLabelText(/click to select/i);
    
    fireEvent.change(input, { target: { files: [invalidFile] } });
    
    await waitFor(() => {
      expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
    });
  });

  it('disables upload when processing', () => {
    render(<ImageUpload onUpload={mockOnUpload} isProcessing={true} />);
    
    const uploadArea = screen.getByText(/Upload Land Record Image/i).closest('div');
    expect(uploadArea).toHaveClass('opacity-50');
  });
});

// ProcessingStatus Component Tests
describe('ProcessingStatus Component', () => {
  it('renders processing status', () => {
    render(
      <ProcessingStatus 
        stages={mockStages} 
        currentStage="ocr" 
        progress={50} 
      />
    );
    
    expect(screen.getByText(/Processing OCR/i)).toBeInTheDocument();
  });

  it('displays progress percentage', () => {
    render(
      <ProcessingStatus 
        stages={mockStages} 
        currentStage="cleaning" 
        progress={75} 
      />
    );
    
    expect(screen.getByText(/75%/i)).toBeInTheDocument();
  });

  it('shows all stages', () => {
    render(
      <ProcessingStatus 
        stages={mockStages} 
        currentStage="transliteration" 
        progress={90} 
      />
    );
    
    expect(screen.getByText(/preprocessing/i)).toBeInTheDocument();
    expect(screen.getByText(/ocr/i)).toBeInTheDocument();
    expect(screen.getByText(/cleaning/i)).toBeInTheDocument();
  });

  it('highlights current stage', () => {
    render(
      <ProcessingStatus 
        stages={mockStages} 
        currentStage="ocr" 
        progress={40} 
      />
    );
    
    const ocrStage = screen.getByText(/ocr/i).closest('div');
    expect(ocrStage).toHaveClass(/processing/);
  });
});

// ResultsDisplay Component Tests
describe('ResultsDisplay Component', () => {
  const mockOnExport = vi.fn();
  const mockOnReset = vi.fn();

  beforeEach(() => {
    mockOnExport.mockClear();
    mockOnReset.mockClear();
  });

  it('renders results display', () => {
    render(
      <ResultsDisplay 
        result={mockResult} 
        onExport={mockOnExport} 
        onReset={mockOnReset} 
      />
    );
    
    expect(screen.getByText(/OCR Results/i)).toBeInTheDocument();
  });

  it('displays all tabs', () => {
    render(
      <ResultsDisplay 
        result={mockResult} 
        onExport={mockOnExport} 
        onReset={mockOnReset} 
      />
    );
    
    expect(screen.getByText(/Raw OCR/i)).toBeInTheDocument();
    expect(screen.getByText(/Cleaned Text/i)).toBeInTheDocument();
    expect(screen.getByText(/Transliterated/i)).toBeInTheDocument();
    expect(screen.getByText(/Metadata/i)).toBeInTheDocument();
  });

  it('switches between tabs', async () => {
    render(
      <ResultsDisplay 
        result={mockResult} 
        onExport={mockOnExport} 
        onReset={mockOnReset} 
      />
    );
    
    const cleanedTab = screen.getByText(/Cleaned Text/i);
    fireEvent.click(cleanedTab);
    
    await waitFor(() => {
      expect(screen.getByText(mockResult.cleaned_text)).toBeInTheDocument();
    });
  });

  it('calls export function', () => {
    render(
      <ResultsDisplay 
        result={mockResult} 
        onExport={mockOnExport} 
        onReset={mockOnReset} 
      />
    );
    
    const exportButton = screen.getByText(/Export JSON/i);
    fireEvent.click(exportButton);
    
    expect(mockOnExport).toHaveBeenCalled();
  });

  it('displays metadata correctly', async () => {
    render(
      <ResultsDisplay 
        result={mockResult} 
        onExport={mockOnExport} 
        onReset={mockOnReset} 
      />
    );
    
    const metadataTab = screen.getByText(/Metadata/i);
    fireEvent.click(metadataTab);
    
    await waitFor(() => {
      expect(screen.getByText(/Language/i)).toBeInTheDocument();
      expect(screen.getByText(/Confidence/i)).toBeInTheDocument();
    });
  });
});

// ComparisonView Component Tests
describe('ComparisonView Component', () => {
  it('renders comparison view', () => {
    render(<ComparisonView result={mockResult} imageUrl="/test.jpg" />);
    
    expect(screen.getByText(/Comparison View/i)).toBeInTheDocument();
  });

  it('shows no results message when result is null', () => {
    render(<ComparisonView result={null} imageUrl={null} />);
    
    expect(screen.getByText(/No results to compare/i)).toBeInTheDocument();
  });

  it('displays left and right panels', () => {
    render(<ComparisonView result={mockResult} imageUrl="/test.jpg" />);
    
    expect(screen.getByText(/Left View/i)).toBeInTheDocument();
    expect(screen.getByText(/Right View/i)).toBeInTheDocument();
  });

  it('has quick comparison buttons', () => {
    render(<ComparisonView result={mockResult} imageUrl="/test.jpg" />);
    
    expect(screen.getByText(/Compare Raw vs Cleaned/i)).toBeInTheDocument();
    expect(screen.getByText(/Compare Cleaned vs Transliterated/i)).toBeInTheDocument();
  });
});

// Export Utilities Tests
describe('Export Utilities', () => {
  it('exports as JSON', async () => {
    const { exportAsJSON } = await import('../src/utils/exportUtils');
    
    const result = exportAsJSON(mockResult, 'test.json');
    expect(result.success).toBe(true);
  });

  it('exports as TXT', async () => {
    const { exportAsTXT } = await import('../src/utils/exportUtils');
    
    const result = exportAsTXT('Test text', 'test.txt');
    expect(result.success).toBe(true);
  });

  it('exports as CSV', async () => {
    const { exportAsCSV } = await import('../src/utils/exportUtils');
    
    const result = exportAsCSV(mockResult, 'test.csv');
    expect(result.success).toBe(true);
  });

  it('copies to clipboard', async () => {
    const { copyToClipboard } = await import('../src/utils/exportUtils');
    
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn(() => Promise.resolve())
      }
    });
    
    const result = await copyToClipboard('Test text');
    expect(result.success).toBe(true);
  });
});
