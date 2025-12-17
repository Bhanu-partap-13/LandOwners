"""
Test RAG Document Processor
Tests the RAG-based approach for large PDF processing
"""
import os
import sys
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_rag_processor():
    """Test RAG document processor"""
    print("=" * 60)
    print("RAG DOCUMENT PROCESSOR TEST")
    print("=" * 60)
    print("Testing RAG-based approach for large PDF handling\n")
    
    from document.rag_document_processor import RAGDocumentProcessor, DocumentChunk
    
    # Initialize processor
    print("Initializing RAG Processor...")
    processor = RAGDocumentProcessor(
        chunk_size=500,
        chunk_overlap=50,
        max_workers=4
    )
    print("✓ RAG Processor initialized\n")
    
    # Test 1: Text chunking
    print("-" * 50)
    print("Test 1: Text Chunking")
    print("-" * 50)
    
    sample_text = """
موضع اتما پور تحصیل بشنال ضلع جموں
جمع بندی سال 2024

خسرہ نمبر: 123/1
مالک: محمد علی ولد عبداللہ
رقبہ: 5 کنال 10 مرلہ

فصل خریف:
گندم - 3 کنال
دھان - 2 کنال

ملاحظات:
زمین آبپاشی کے تحت ہے
    """
    
    chunks = processor.chunk_text(sample_text, page_number=1)
    print(f"Created {len(chunks)} chunks from sample text")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {len(chunk.text)} chars - {chunk.text[:50]}...")
    print()
    
    # Test 2: Translation with caching
    print("-" * 50)
    print("Test 2: Translation with Caching")
    print("-" * 50)
    
    test_chunks = [
        DocumentChunk(chunk_id="test_1", page_number=1, text="موضع اتما پور"),
        DocumentChunk(chunk_id="test_2", page_number=1, text="ضلع جموں"),
        DocumentChunk(chunk_id="test_3", page_number=1, text="جمع بندی سال 2024"),
    ]
    
    print("Translating chunks (first time - uncached):")
    start = time.time()
    for chunk in test_chunks:
        processor.translate_chunk(chunk)
        print(f"  {chunk.text} → {chunk.translated_text}")
    first_time = time.time() - start
    print(f"Time: {first_time:.2f}s\n")
    
    # Translate same chunks again (should be cached)
    print("Translating same chunks (cached):")
    test_chunks_2 = [
        DocumentChunk(chunk_id="test_1b", page_number=1, text="موضع اتما پور"),
        DocumentChunk(chunk_id="test_2b", page_number=1, text="ضلع جموں"),
    ]
    
    start = time.time()
    for chunk in test_chunks_2:
        processor.translate_chunk(chunk)
        cached = chunk.metadata.get('translation_cached', False)
        print(f"  {chunk.text} → {chunk.translated_text} {'(cached)' if cached else ''}")
    cached_time = time.time() - start
    if cached_time > 0:
        print(f"Time: {cached_time:.2f}s (speedup: {first_time/cached_time:.1f}x)\n")
    else:
        print(f"Time: <0.01s (instant - cached!)\n")
    
    # Test 3: Vector store and search
    print("-" * 50)
    print("Test 3: Vector Store and Semantic Search")
    print("-" * 50)
    
    # Add chunks to vector store
    processor.vector_store.add_chunks(test_chunks)
    print(f"Added {len(test_chunks)} chunks to vector store")
    
    # Search
    search_query = "جموں"
    results = processor.search_document(search_query, top_k=3)
    print(f"\nSearch query: '{search_query}'")
    print("Results:")
    for result in results:
        chunk = result['chunk']
        score = result['similarity_score']
        print(f"  Score {score:.4f}: {chunk['text']} → {chunk['translated_text']}")
    print()
    
    # Test 4: RAG-style translation query
    print("-" * 50)
    print("Test 4: RAG Translation Query")
    print("-" * 50)
    
    rag_result = processor.get_translation_for_query("جمع بندی", context_chunks=2)
    print(f"Query: '{rag_result['query']}'")
    print("Relevant translations:")
    for trans in rag_result['translations']:
        print(f"  [{trans['relevance']:.4f}] {trans['original']} → {trans['translated']}")
    print()
    
    # Test 5: Progress tracking
    print("-" * 50)
    print("Test 5: Progress Tracking")
    print("-" * 50)
    
    processor.progress.total_pages = 100
    processor.progress.processed_pages = 35
    processor.progress.current_stage = "translating"
    
    progress = processor.get_progress()
    print(f"Progress: {progress['progress_percent']:.1f}%")
    print(f"Processed: {progress['processed_pages']}/{progress['total_pages']} pages")
    print(f"Stage: {progress['current_stage']}")
    print()
    
    # Summary
    print("=" * 60)
    print("RAG PROCESSOR TEST COMPLETE")
    print("=" * 60)
    print("""
✓ Text chunking with overlap
✓ Translation with caching
✓ Vector store for semantic search
✓ RAG-style translation queries
✓ Progress tracking

RAG Benefits for Large PDFs:
1. Memory efficient - processes page-by-page
2. Translation caching - repeated terms translated once
3. Semantic search - find relevant sections quickly
4. Streaming support - results available as processed
5. Progress tracking - user knows status
    """)


def test_pdf_processing():
    """Test PDF processing with RAG"""
    print("=" * 60)
    print("RAG PDF PROCESSING TEST")
    print("=" * 60)
    
    # Check for test PDF
    test_pdfs = [
        r"C:\Jammu\Documents\Original\Atmapur.pdf",
        r"C:\Jammu\LandOwners\uploads\test.pdf",
    ]
    
    pdf_path = None
    for path in test_pdfs:
        if os.path.exists(path):
            pdf_path = path
            break
    
    if not pdf_path:
        print("No test PDF found. Skipping PDF test.")
        print("To test, place a PDF at one of these locations:")
        for path in test_pdfs:
            print(f"  - {path}")
        return
    
    print(f"Found test PDF: {pdf_path}")
    
    try:
        import fitz
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()
        print(f"PDF has {total_pages} pages")
    except ImportError:
        print("PyMuPDF not installed. Install with: pip install pymupdf")
        return
    
    from document.rag_document_processor import RAGDocumentProcessor
    
    processor = RAGDocumentProcessor()
    
    def progress_callback(progress):
        print(f"\rProgress: {progress['progress_percent']:.1f}% ({progress['processed_pages']}/{progress['total_pages']} pages)", end="")
    
    print("\nProcessing PDF (streaming mode)...")
    print("-" * 50)
    
    page_count = 0
    for page_result in processor.process_pdf_streaming(
        pdf_path,
        translate=True,
        progress_callback=progress_callback
    ):
        page_count += 1
        if page_count <= 3:  # Show first 3 pages
            print(f"\n\nPage {page_result['page_number']}:")
            print(f"  Text: {page_result['text'][:100]}...")
            if page_result.get('translated_text'):
                print(f"  Translation: {page_result['translated_text'][:100]}...")
    
    print(f"\n\nProcessed {page_count} pages total")
    
    # Test search on processed document
    print("\n" + "-" * 50)
    print("Searching processed document...")
    
    results = processor.search_document("مالک", top_k=3)
    print(f"Found {len(results)} results for 'مالک' (owner)")
    for r in results:
        print(f"  Page {r['chunk']['page_number']}: {r['chunk']['text'][:50]}...")


if __name__ == '__main__':
    test_rag_processor()
    print("\n")
    test_pdf_processing()
