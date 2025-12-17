"""
RAG (Retrieval-Augmented Generation) Document Processor
Efficient handling of large PDFs (200+ pages) using chunking and embeddings

This module provides:
1. Document chunking for large PDFs
2. Vector embeddings for efficient retrieval
3. Incremental OCR processing
4. Cached translation with semantic search
5. Progress tracking for long-running operations
"""

import os
import hashlib
import json
import logging
import time
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Generator, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of a document"""
    chunk_id: str
    page_number: int
    text: str
    translated_text: str = ""
    embedding: Optional[np.ndarray] = None
    ocr_confidence: float = 0.0
    translation_confidence: float = 0.0
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'chunk_id': self.chunk_id,
            'page_number': self.page_number,
            'text': self.text,
            'translated_text': self.translated_text,
            'ocr_confidence': self.ocr_confidence,
            'translation_confidence': self.translation_confidence,
            'metadata': self.metadata
        }


@dataclass
class ProcessingProgress:
    """Track processing progress for large documents"""
    total_pages: int = 0
    processed_pages: int = 0
    total_chunks: int = 0
    processed_chunks: int = 0
    current_stage: str = "initializing"
    start_time: float = field(default_factory=time.time)
    errors: List[str] = field(default_factory=list)
    
    @property
    def progress_percent(self) -> float:
        if self.total_pages == 0:
            return 0.0
        return (self.processed_pages / self.total_pages) * 100
    
    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    @property
    def estimated_remaining(self) -> float:
        if self.processed_pages == 0:
            return 0.0
        rate = self.processed_pages / self.elapsed_time
        remaining_pages = self.total_pages - self.processed_pages
        return remaining_pages / rate if rate > 0 else 0.0
    
    def to_dict(self) -> Dict:
        return {
            'total_pages': self.total_pages,
            'processed_pages': self.processed_pages,
            'progress_percent': round(self.progress_percent, 2),
            'current_stage': self.current_stage,
            'elapsed_seconds': round(self.elapsed_time, 2),
            'estimated_remaining_seconds': round(self.estimated_remaining, 2),
            'errors': self.errors
        }


class SimpleEmbedding:
    """
    Simple embedding generator using TF-IDF or character n-grams
    For production, replace with sentence-transformers or OpenAI embeddings
    """
    
    def __init__(self, embedding_dim: int = 256):
        self.embedding_dim = embedding_dim
        self.vocabulary: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    def _get_ngrams(self, text: str, n: int = 3) -> List[str]:
        """Generate character n-grams from text"""
        text = text.lower().strip()
        ngrams = []
        for i in range(len(text) - n + 1):
            ngrams.append(text[i:i+n])
        return ngrams
    
    def encode(self, text: str) -> np.ndarray:
        """Generate embedding for text using character n-grams"""
        if not text:
            return np.zeros(self.embedding_dim)
        
        # Get n-grams
        ngrams = self._get_ngrams(text, 3)
        
        # Create sparse vector based on hash
        embedding = np.zeros(self.embedding_dim)
        for ngram in ngrams:
            # Use hash to get consistent index
            idx = hash(ngram) % self.embedding_dim
            embedding[idx] += 1
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode multiple texts"""
        return np.array([self.encode(text) for text in texts])
    
    def similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        if emb1 is None or emb2 is None:
            return 0.0
        dot = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)


class VectorStore:
    """
    Simple in-memory vector store for document chunks
    For production, use FAISS, Pinecone, or ChromaDB
    """
    
    def __init__(self, embedding_model: SimpleEmbedding = None):
        self.embedder = embedding_model or SimpleEmbedding()
        self.chunks: List[DocumentChunk] = []
        self.embeddings: Optional[np.ndarray] = None
        self._lock = threading.Lock()
    
    def add_chunk(self, chunk: DocumentChunk) -> None:
        """Add a chunk to the store"""
        with self._lock:
            if chunk.embedding is None:
                chunk.embedding = self.embedder.encode(chunk.text)
            self.chunks.append(chunk)
            # Rebuild embeddings matrix
            self.embeddings = np.array([c.embedding for c in self.chunks])
    
    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Add multiple chunks"""
        with self._lock:
            for chunk in chunks:
                if chunk.embedding is None:
                    chunk.embedding = self.embedder.encode(chunk.text)
                self.chunks.append(chunk)
            self.embeddings = np.array([c.embedding for c in self.chunks])
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Search for similar chunks"""
        if not self.chunks:
            return []
        
        query_embedding = self.embedder.encode(query)
        
        # Calculate similarities
        similarities = []
        for i, chunk in enumerate(self.chunks):
            sim = self.embedder.similarity(query_embedding, chunk.embedding)
            similarities.append((chunk, sim))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def get_by_page(self, page_number: int) -> List[DocumentChunk]:
        """Get all chunks for a specific page"""
        return [c for c in self.chunks if c.page_number == page_number]
    
    def get_all(self) -> List[DocumentChunk]:
        """Get all chunks"""
        return self.chunks.copy()
    
    def clear(self) -> None:
        """Clear all chunks"""
        with self._lock:
            self.chunks = []
            self.embeddings = None
    
    def save(self, filepath: str) -> None:
        """Save vector store to disk"""
        with self._lock:
            data = {
                'chunks': [c.to_dict() for c in self.chunks],
                'embeddings': self.embeddings.tolist() if self.embeddings is not None else None
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
    
    def load(self, filepath: str) -> None:
        """Load vector store from disk"""
        with self._lock:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.chunks = []
            for chunk_data in data['chunks']:
                chunk = DocumentChunk(
                    chunk_id=chunk_data['chunk_id'],
                    page_number=chunk_data['page_number'],
                    text=chunk_data['text'],
                    translated_text=chunk_data.get('translated_text', ''),
                    ocr_confidence=chunk_data.get('ocr_confidence', 0.0),
                    translation_confidence=chunk_data.get('translation_confidence', 0.0),
                    metadata=chunk_data.get('metadata', {})
                )
                self.chunks.append(chunk)
            
            if data.get('embeddings'):
                self.embeddings = np.array(data['embeddings'])
                for i, chunk in enumerate(self.chunks):
                    chunk.embedding = self.embeddings[i]


class RAGDocumentProcessor:
    """
    RAG-based document processor for efficient large PDF handling
    
    Features:
    - Chunked processing (page-by-page or section-by-section)
    - Vector embeddings for semantic search
    - Translation caching
    - Progress tracking
    - Parallel processing support
    """
    
    def __init__(
        self,
        cache_dir: str = None,
        chunk_size: int = 500,  # Characters per chunk
        chunk_overlap: int = 50,  # Overlap between chunks
        max_workers: int = 4,
        embedding_dim: int = 256
    ):
        """
        Initialize RAG processor
        
        Args:
            cache_dir: Directory for caching processed documents
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between consecutive chunks
            max_workers: Maximum parallel workers
            embedding_dim: Dimension of embeddings
        """
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(__file__), '..', 'cache', 'rag'
        )
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_workers = max_workers
        
        # Initialize components
        self.embedder = SimpleEmbedding(embedding_dim)
        self.vector_store = VectorStore(self.embedder)
        
        # Translation cache
        self.translation_cache: Dict[str, str] = {}
        self._cache_lock = threading.Lock()
        
        # Progress tracking
        self.progress = ProcessingProgress()
        
        # OCR and translation will be lazily imported
        self._ocr_engine = None
        self._translator = None
        
        logger.info(f"RAG Document Processor initialized (cache: {self.cache_dir})")
    
    def _get_ocr_engine(self):
        """Lazy load OCR engine"""
        if self._ocr_engine is None:
            try:
                from ocr.ocr_engine import MultiLanguageOCR
                self._ocr_engine = MultiLanguageOCR()
            except ImportError:
                logger.warning("OCR engine not available")
        return self._ocr_engine
    
    def _get_translator(self):
        """Lazy load translator"""
        if self._translator is None:
            try:
                from translation.indictrans_translator import IndicTransTranslator
                self._translator = IndicTransTranslator(direction='indic-en')
            except ImportError:
                logger.warning("IndicTransTranslator not available")
        return self._translator
    
    def _generate_doc_hash(self, filepath: str) -> str:
        """Generate hash for document caching"""
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _get_cache_path(self, doc_hash: str) -> str:
        """Get cache file path for a document"""
        return os.path.join(self.cache_dir, f"{doc_hash}.json")
    
    def _load_cached(self, doc_hash: str) -> Optional[Dict]:
        """Load cached document data"""
        cache_path = self._get_cache_path(doc_hash)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        return None
    
    def _save_cache(self, doc_hash: str, data: Dict) -> None:
        """Save document data to cache"""
        cache_path = self._get_cache_path(doc_hash)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def chunk_text(self, text: str, page_number: int = 0) -> List[DocumentChunk]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to chunk
            page_number: Page number for metadata
            
        Returns:
            List of DocumentChunk objects
        """
        if not text:
            return []
        
        chunks = []
        text = text.strip()
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        chunk_idx = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk size, save current and start new
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunk_id = f"p{page_number}_c{chunk_idx}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    page_number=page_number,
                    text=current_chunk.strip()
                ))
                
                # Keep overlap from end of current chunk
                if self.chunk_overlap > 0:
                    current_chunk = current_chunk[-self.chunk_overlap:] + " " + para
                else:
                    current_chunk = para
                chunk_idx += 1
            else:
                current_chunk = current_chunk + "\n\n" + para if current_chunk else para
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunk_id = f"p{page_number}_c{chunk_idx}"
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                page_number=page_number,
                text=current_chunk.strip()
            ))
        
        return chunks
    
    def process_pdf_page(
        self,
        image_or_path,
        page_number: int,
        ocr_options: Dict = None
    ) -> List[DocumentChunk]:
        """
        Process a single PDF page
        
        Args:
            image_or_path: Image array or path to image
            page_number: Page number
            ocr_options: OCR configuration options
            
        Returns:
            List of chunks from this page
        """
        ocr = self._get_ocr_engine()
        if ocr is None:
            logger.error("OCR engine not available")
            return []
        
        try:
            # Perform OCR
            ocr_result = ocr.process_image(image_or_path, preprocess=True)
            text = ocr_result.get('text', '')
            confidence = ocr_result.get('confidence', 0)
            
            # Chunk the text
            chunks = self.chunk_text(text, page_number)
            
            # Set OCR confidence for all chunks
            for chunk in chunks:
                chunk.ocr_confidence = confidence
                chunk.metadata['ocr_method'] = ocr_result.get('method', 'tesseract')
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing page {page_number}: {e}")
            self.progress.errors.append(f"Page {page_number}: {str(e)}")
            return []
    
    def translate_chunk(self, chunk: DocumentChunk, src_lang: str = 'ur', tgt_lang: str = 'en') -> DocumentChunk:
        """
        Translate a single chunk with caching
        
        Args:
            chunk: Document chunk to translate
            src_lang: Source language
            tgt_lang: Target language
            
        Returns:
            Chunk with translated_text filled
        """
        # Check cache first
        cache_key = hashlib.md5(chunk.text.encode()).hexdigest()
        
        with self._cache_lock:
            if cache_key in self.translation_cache:
                chunk.translated_text = self.translation_cache[cache_key]
                chunk.translation_confidence = 0.95
                chunk.metadata['translation_cached'] = True
                return chunk
        
        # Translate
        translator = self._get_translator()
        if translator is None:
            chunk.translated_text = chunk.text  # Return original if no translator
            chunk.translation_confidence = 0.0
            return chunk
        
        try:
            result = translator.translate(chunk.text, src_lang, tgt_lang)
            chunk.translated_text = result
            chunk.translation_confidence = 0.95
            chunk.metadata['translation_method'] = 'indictrans2'
            
            # Cache the translation
            with self._cache_lock:
                self.translation_cache[cache_key] = result
            
        except Exception as e:
            logger.error(f"Translation error for chunk {chunk.chunk_id}: {e}")
            chunk.translated_text = chunk.text
            chunk.translation_confidence = 0.0
            chunk.metadata['translation_error'] = str(e)
        
        return chunk
    
    def process_pdf_streaming(
        self,
        pdf_path: str,
        translate: bool = True,
        src_lang: str = 'ur',
        tgt_lang: str = 'en',
        use_cache: bool = True,
        progress_callback: callable = None
    ) -> Generator[Dict, None, None]:
        """
        Process PDF page-by-page, yielding results as they're ready
        
        This is the key RAG method - processes large PDFs incrementally
        without loading everything into memory
        
        Args:
            pdf_path: Path to PDF file
            translate: Whether to translate text
            src_lang: Source language
            tgt_lang: Target language
            use_cache: Use cached results if available
            progress_callback: Callback function for progress updates
            
        Yields:
            Dict with page results as they become available
        """
        import fitz  # PyMuPDF
        
        # Generate document hash for caching
        doc_hash = self._generate_doc_hash(pdf_path)
        
        # Check for cached results
        if use_cache:
            cached = self._load_cached(doc_hash)
            if cached:
                logger.info(f"Loading cached results for {pdf_path}")
                for page_data in cached.get('pages', []):
                    yield page_data
                return
        
        # Open PDF
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        # Initialize progress
        self.progress = ProcessingProgress()
        self.progress.total_pages = total_pages
        self.progress.current_stage = "processing"
        
        # Clear vector store for new document
        self.vector_store.clear()
        
        all_pages_data = []
        
        for page_num in range(total_pages):
            page_start_time = time.time()
            self.progress.current_stage = f"page_{page_num + 1}"
            
            try:
                # Get page as image
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale for better OCR
                img_data = pix.tobytes("png")
                
                # Save temporarily for OCR
                temp_img_path = os.path.join(self.cache_dir, f"temp_page_{page_num}.png")
                with open(temp_img_path, 'wb') as f:
                    f.write(img_data)
                
                # Process page
                chunks = self.process_pdf_page(temp_img_path, page_num)
                
                # Clean up temp file
                try:
                    os.remove(temp_img_path)
                except:
                    pass
                
                # Translate chunks if requested
                if translate and chunks:
                    for chunk in chunks:
                        self.translate_chunk(chunk, src_lang, tgt_lang)
                
                # Add to vector store
                self.vector_store.add_chunks(chunks)
                
                # Prepare page result
                page_result = {
                    'page_number': page_num + 1,
                    'chunks': [c.to_dict() for c in chunks],
                    'text': '\n\n'.join([c.text for c in chunks]),
                    'translated_text': '\n\n'.join([c.translated_text for c in chunks]) if translate else '',
                    'avg_ocr_confidence': sum(c.ocr_confidence for c in chunks) / len(chunks) if chunks else 0,
                    'processing_time': time.time() - page_start_time
                }
                
                all_pages_data.append(page_result)
                
                # Update progress
                self.progress.processed_pages = page_num + 1
                self.progress.total_chunks += len(chunks)
                self.progress.processed_chunks += len(chunks)
                
                # Call progress callback
                if progress_callback:
                    progress_callback(self.progress.to_dict())
                
                # Yield result immediately
                yield page_result
                
            except Exception as e:
                logger.error(f"Error processing page {page_num + 1}: {e}")
                self.progress.errors.append(f"Page {page_num + 1}: {str(e)}")
                yield {
                    'page_number': page_num + 1,
                    'error': str(e),
                    'chunks': [],
                    'text': '',
                    'translated_text': ''
                }
        
        doc.close()
        
        # Cache results
        if use_cache:
            self._save_cache(doc_hash, {
                'pages': all_pages_data,
                'total_pages': total_pages,
                'doc_hash': doc_hash
            })
        
        self.progress.current_stage = "complete"
    
    def process_pdf_batch(
        self,
        pdf_path: str,
        translate: bool = True,
        src_lang: str = 'ur',
        tgt_lang: str = 'en',
        batch_size: int = 10,
        use_cache: bool = True,
        progress_callback: callable = None
    ) -> Dict:
        """
        Process PDF in batches for better throughput on large documents
        
        Args:
            pdf_path: Path to PDF file
            translate: Whether to translate
            src_lang: Source language
            tgt_lang: Target language
            batch_size: Number of pages to process in parallel
            use_cache: Use caching
            progress_callback: Progress callback
            
        Returns:
            Complete document result
        """
        import fitz
        
        doc_hash = self._generate_doc_hash(pdf_path)
        
        # Check cache
        if use_cache:
            cached = self._load_cached(doc_hash)
            if cached:
                return cached
        
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        self.progress = ProcessingProgress()
        self.progress.total_pages = total_pages
        self.progress.current_stage = "batch_processing"
        
        self.vector_store.clear()
        all_pages_data = []
        
        # Process in batches
        for batch_start in range(0, total_pages, batch_size):
            batch_end = min(batch_start + batch_size, total_pages)
            batch_pages = list(range(batch_start, batch_end))
            
            # Extract images for batch
            batch_images = []
            for page_num in batch_pages:
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                temp_path = os.path.join(self.cache_dir, f"temp_batch_{page_num}.png")
                with open(temp_path, 'wb') as f:
                    f.write(img_data)
                batch_images.append((page_num, temp_path))
            
            # Process batch in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self.process_pdf_page, img_path, page_num): page_num
                    for page_num, img_path in batch_images
                }
                
                batch_results = {}
                for future in as_completed(futures):
                    page_num = futures[future]
                    try:
                        chunks = future.result()
                        batch_results[page_num] = chunks
                    except Exception as e:
                        logger.error(f"Batch error page {page_num}: {e}")
                        batch_results[page_num] = []
            
            # Translate batch results
            if translate:
                for page_num, chunks in batch_results.items():
                    for chunk in chunks:
                        self.translate_chunk(chunk, src_lang, tgt_lang)
            
            # Add to results and vector store
            for page_num in sorted(batch_results.keys()):
                chunks = batch_results[page_num]
                self.vector_store.add_chunks(chunks)
                
                all_pages_data.append({
                    'page_number': page_num + 1,
                    'chunks': [c.to_dict() for c in chunks],
                    'text': '\n\n'.join([c.text for c in chunks]),
                    'translated_text': '\n\n'.join([c.translated_text for c in chunks]) if translate else ''
                })
            
            # Clean up temp files
            for _, img_path in batch_images:
                try:
                    os.remove(img_path)
                except:
                    pass
            
            # Update progress
            self.progress.processed_pages = batch_end
            if progress_callback:
                progress_callback(self.progress.to_dict())
        
        doc.close()
        
        # Build final result
        result = {
            'doc_hash': doc_hash,
            'total_pages': total_pages,
            'pages': all_pages_data,
            'full_text': '\n\n---\n\n'.join([p['text'] for p in all_pages_data]),
            'full_translation': '\n\n---\n\n'.join([p['translated_text'] for p in all_pages_data]) if translate else ''
        }
        
        # Cache
        if use_cache:
            self._save_cache(doc_hash, result)
        
        self.progress.current_stage = "complete"
        return result
    
    def search_document(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search processed document using semantic similarity
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of matching chunks with scores
        """
        results = self.vector_store.search(query, top_k)
        return [
            {
                'chunk': chunk.to_dict(),
                'similarity_score': round(score, 4)
            }
            for chunk, score in results
        ]
    
    def get_translation_for_query(self, query: str, context_chunks: int = 3) -> Dict:
        """
        RAG-style translation: find relevant chunks and return their translations
        
        Args:
            query: Query text (in source language)
            context_chunks: Number of context chunks to return
            
        Returns:
            Dict with relevant translations and context
        """
        # Search for relevant chunks
        results = self.vector_store.search(query, context_chunks)
        
        if not results:
            return {
                'query': query,
                'translations': [],
                'context': []
            }
        
        return {
            'query': query,
            'translations': [
                {
                    'original': chunk.text,
                    'translated': chunk.translated_text,
                    'confidence': chunk.translation_confidence,
                    'relevance': round(score, 4)
                }
                for chunk, score in results
            ],
            'context': [chunk.text for chunk, _ in results]
        }
    
    def get_progress(self) -> Dict:
        """Get current processing progress"""
        return self.progress.to_dict()
    
    def clear_cache(self, doc_hash: str = None) -> None:
        """Clear cache for a specific document or all cache"""
        if doc_hash:
            cache_path = self._get_cache_path(doc_hash)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        else:
            # Clear all cache
            for f in os.listdir(self.cache_dir):
                if f.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, f))
        
        # Clear translation cache
        with self._cache_lock:
            self.translation_cache.clear()


# Convenience functions
def create_rag_processor(cache_dir: str = None) -> RAGDocumentProcessor:
    """Create a new RAG processor instance"""
    return RAGDocumentProcessor(cache_dir=cache_dir)


def process_large_pdf(
    pdf_path: str,
    translate: bool = True,
    streaming: bool = True,
    progress_callback: callable = None
) -> Generator[Dict, None, None] | Dict:
    """
    Convenience function to process large PDF
    
    Args:
        pdf_path: Path to PDF
        translate: Whether to translate
        streaming: Use streaming mode (recommended for large docs)
        progress_callback: Progress callback
        
    Returns:
        Generator if streaming, Dict if not
    """
    processor = RAGDocumentProcessor()
    
    if streaming:
        return processor.process_pdf_streaming(
            pdf_path,
            translate=translate,
            progress_callback=progress_callback
        )
    else:
        return processor.process_pdf_batch(
            pdf_path,
            translate=translate,
            progress_callback=progress_callback
        )
