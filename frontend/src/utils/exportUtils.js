/**
 * Export Utilities
 * Functions to export OCR results in various formats
 */

/**
 * Download content as a file
 */
const downloadFile = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Export as JSON
 */
export const exportAsJSON = (result, filename = 'ocr_result.json') => {
  try {
    const jsonContent = JSON.stringify(result, null, 2);
    downloadFile(jsonContent, filename, 'application/json');
    return { success: true };
  } catch (error) {
    console.error('Error exporting as JSON:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Export as TXT (plain text)
 */
export const exportAsTXT = (text, filename = 'ocr_result.txt') => {
  try {
    downloadFile(text, filename, 'text/plain');
    return { success: true };
  } catch (error) {
    console.error('Error exporting as TXT:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Export as CSV
 */
export const exportAsCSV = (result, filename = 'ocr_result.csv') => {
  try {
    const rows = [
      ['Field', 'Value'],
      ['Raw Text', result.raw_text || ''],
      ['Cleaned Text', result.cleaned_text || ''],
      ['Transliterated Text', result.transliterated_text || ''],
      ['Language', result.language?.detected || ''],
      ['Confidence', result.language?.confidence || ''],
      ['Processing Time', result.processing?.total_time || ''],
      ['Word Count', result.metadata?.word_count || ''],
      ['Character Count', result.metadata?.character_count || ''],
    ];

    const csvContent = rows
      .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
      .join('\n');

    downloadFile(csvContent, filename, 'text/csv');
    return { success: true };
  } catch (error) {
    console.error('Error exporting as CSV:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Export as Markdown
 */
export const exportAsMarkdown = (result, filename = 'ocr_result.md') => {
  try {
    const markdown = `# OCR Result

## Metadata
- **Language**: ${result.language?.detected || 'Unknown'}
- **Confidence**: ${result.language?.confidence || 'N/A'}
- **Processing Time**: ${result.processing?.total_time || 'N/A'}s
- **Word Count**: ${result.metadata?.word_count || 0}
- **Character Count**: ${result.metadata?.character_count || 0}

## Raw OCR Text
\`\`\`
${result.raw_text || 'No text extracted'}
\`\`\`

## Cleaned Text
\`\`\`
${result.cleaned_text || 'No cleaned text available'}
\`\`\`

## Transliterated Text
\`\`\`
${result.transliterated_text || 'No transliteration available'}
\`\`\`

## Processing Stages
${Object.entries(result.processing?.stages || {})
  .map(([stage, data]) => `- **${stage}**: ${data.duration || 0}s`)
  .join('\n')}
`;

    downloadFile(markdown, filename, 'text/markdown');
    return { success: true };
  } catch (error) {
    console.error('Error exporting as Markdown:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Export all formats at once
 */
export const exportAll = (result, baseName = 'ocr_result') => {
  const results = {
    json: exportAsJSON(result, `${baseName}.json`),
    txt: exportAsTXT(result.cleaned_text || result.raw_text, `${baseName}.txt`),
    csv: exportAsCSV(result, `${baseName}.csv`),
    markdown: exportAsMarkdown(result, `${baseName}.md`),
  };

  const allSuccess = Object.values(results).every(r => r.success);
  
  return {
    success: allSuccess,
    results,
  };
};

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text) => {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return { success: true };
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);
      
      return { success: successful };
    }
  } catch (error) {
    console.error('Error copying to clipboard:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Create a detailed report with all information
 */
export const createDetailedReport = (result) => {
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      language: result.language?.detected,
      confidence: result.language?.confidence,
      totalProcessingTime: result.processing?.total_time,
      wordCount: result.metadata?.word_count,
      characterCount: result.metadata?.character_count,
    },
    texts: {
      raw: result.raw_text,
      cleaned: result.cleaned_text,
      transliterated: result.transliterated_text,
    },
    stages: result.processing?.stages || {},
    metadata: result.metadata || {},
  };

  return report;
};

export default {
  exportAsJSON,
  exportAsTXT,
  exportAsCSV,
  exportAsMarkdown,
  exportAll,
  copyToClipboard,
  createDetailedReport,
};
