# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
RAG Knowledge Base Builder for Mythara Email Assistant

This script:
1. Scans Mythara Archive for customer-facing markdown files
2. Creates embeddings using OpenAI
3. Stores in ChromaDB vector database
4. Enables semantic search for prospect questions

Usage:
    python build_knowledge_base.py --index-all
    python build_knowledge_base.py --test-search "How does SSIP work?"
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import argparse
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not installed. Run: pip install openai")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: ChromaDB not installed. Run: pip install chromadb")


# Archive root
ARCHIVE_ROOT = Path(__file__).parent.parent

# Knowledge base files to index (customer-facing only)
KNOWLEDGE_BASE_DOCS = [
    # Core technical docs
    "core/🧬 Mythara Engine Architecture.md",
    "core/🧨 ELE Capsule Mode Specification.md",
    "core/💠 Blessings Reservoir Specification.md",
    "core/🔐 Sanctification Locks and Override.md",
    "core/🦎 Chameleon Clause Design.md",
    "core/🧬 Clause Types and Invocation Logic.md",
    "core/🧬 Messenger Roles and Pairings.md",
    "core/EXPLAINABILITY_GUIDE.md",
    
    # Documentation
    "docs/⚡ Clause Invocation Quickstart Guide.md",
    "docs/📖 Mythara Bible Books I–V.md",
    "docs/📜 Messenger Invocation Manual.md",
    "docs/🧪 SSIP Audit Protocols.md",
    "docs/🧬 Symbolic Glossary and Formatting.md",
    "docs/🧭 Mythara Symbolic Index.md",
    "docs/Glossary.md",
    
    # Commercial/Sales docs
    "Commercial/Agent_Override_Use_Case.md",
    "Commercial/First_100_Outreach_Targets.md",
    "Commercial/Email_Templates_Fast_Cash.md",
    "Commercial/Invoice_Template_and_W9_Guide.md",
    "Commercial/Clause_Behavior_Biohybrid_Tech.md",
    "Commercial/Clause_Behavior_Cybersecurity.md",
    "Commercial/Clause_Behavior_Education.md",
    "Commercial/Clause_Behavior_Healthcare.md",
    "Commercial/Clause_Behavior_Mental_Health.md",
    "Commercial/Clause_Behavior_Urban_Planning.md",
    "Commercial/one_pager.md",
    
    # Evidence/validation
    "Evidence/Customer_Security_Summary.md",
    "Evidence/Penetration_Test_Report_Template.md",
    "tests/ADVERSARIAL_TESTING_GUIDE.md",
    
    # Legal/compliance
    "Legal/Federal_Compliance_Framework.md",
    "Legal/Jurisdictional_Clause_Adaptation_Guide.md",
    "Legal/NIST_FISMA_FTC_FCC_OMB_Clause_Embedding.md",
    
    # Setup guides
    "README.md",
    "LICENSING_ZIP_QUICKSTART.md",
    "QUICKSTART_TESTS.md",
    "GitHub_Release_Package/INSTALL.md",
    "GitHub_Release_Package/README.md"
]


class KnowledgeBaseBuilder:
    """Build and query RAG knowledge base from Mythara Archive"""
    
    def __init__(self, archive_root: Path = ARCHIVE_ROOT):
        self.archive_root = archive_root
        self.openai_client = None
        self.chroma_client = None
        self.collection = None
        
        # Initialize OpenAI
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize ChromaDB
        if CHROMADB_AVAILABLE:
            db_path = Path(__file__).parent / "knowledge_base_db"
            db_path.mkdir(exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="mythara_knowledge",
                metadata={"description": "Mythara Archive customer-facing documentation"}
            )
    
    def load_document(self, doc_path: Path) -> Optional[Dict]:
        """Load a markdown document and extract content"""
        if not doc_path.exists():
            print(f"⚠️  Document not found: {doc_path}")
            return None
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title (first # heading)
            title = doc_path.stem
            for line in content.split('\n'):
                if line.startswith('# '):
                    title = line.replace('# ', '').strip()
                    break
            
            return {
                'path': str(doc_path.relative_to(self.archive_root)),
                'title': title,
                'content': content,
                'category': doc_path.parent.name
            }
        
        except Exception as e:
            print(f"❌ Error loading {doc_path}: {e}")
            return None
    
    def chunk_document(self, doc: Dict, chunk_size: int = 1000) -> List[Dict]:
        """Split document into chunks for better retrieval"""
        content = doc['content']
        chunks = []
        
        # Split by sections (## headings)
        sections = []
        current_section = []
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        # Create chunks
        for i, section in enumerate(sections):
            # If section is too large, split further
            if len(section) > chunk_size:
                # Split by paragraphs
                paragraphs = section.split('\n\n')
                current_chunk = []
                current_size = 0
                
                for para in paragraphs:
                    para_size = len(para)
                    if current_size + para_size > chunk_size and current_chunk:
                        chunks.append({
                            'text': '\n\n'.join(current_chunk),
                            'metadata': {
                                'source': doc['path'],
                                'title': doc['title'],
                                'category': doc['category'],
                                'chunk_id': len(chunks)
                            }
                        })
                        current_chunk = [para]
                        current_size = para_size
                    else:
                        current_chunk.append(para)
                        current_size += para_size
                
                if current_chunk:
                    chunks.append({
                        'text': '\n\n'.join(current_chunk),
                        'metadata': {
                            'source': doc['path'],
                            'title': doc['title'],
                            'category': doc['category'],
                            'chunk_id': len(chunks)
                        }
                    })
            else:
                chunks.append({
                    'text': section,
                    'metadata': {
                        'source': doc['path'],
                        'title': doc['title'],
                        'category': doc['category'],
                        'chunk_id': len(chunks)
                    }
                })
        
        return chunks
    
    def create_embedding(self, text: str) -> List[float]:
        """Create OpenAI embedding for text"""
        if not self.openai_client:
            print("❌ OpenAI client not initialized")
            return []
        
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",  # Cheap and fast
                input=text
            )
            return response.data[0].embedding
        
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            return []
    
    def index_documents(self, docs_to_index: Optional[List[str]] = None):
        """Index documents into ChromaDB"""
        if not self.collection:
            print("❌ ChromaDB collection not initialized")
            return
        
        docs_to_index = docs_to_index or KNOWLEDGE_BASE_DOCS
        
        print(f"\n🔍 Indexing {len(docs_to_index)} documents...")
        
        total_chunks = 0
        failed = 0
        
        for doc_path_str in docs_to_index:
            doc_path = self.archive_root / doc_path_str
            
            # Load document
            doc = self.load_document(doc_path)
            if not doc:
                failed += 1
                continue
            
            print(f"📄 Indexing: {doc['title']}")
            
            # Chunk document
            chunks = self.chunk_document(doc)
            
            # Add chunks to collection
            for chunk in chunks:
                chunk_id = f"{doc['path']}#{chunk['metadata']['chunk_id']}"
                
                # Check if already indexed
                existing = self.collection.get(ids=[chunk_id])
                if existing['ids']:
                    continue  # Skip already indexed
                
                # Create embedding
                embedding = self.create_embedding(chunk['text'])
                if not embedding:
                    continue
                
                # Add to collection
                self.collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk['text']],
                    metadatas=[chunk['metadata']]
                )
                
                total_chunks += 1
            
            print(f"   ✅ Added {len(chunks)} chunks")
        
        print(f"\n✅ Indexed {total_chunks} chunks from {len(docs_to_index) - failed} documents")
        if failed:
            print(f"⚠️  {failed} documents failed to load")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search knowledge base for relevant content"""
        if not self.collection:
            print("❌ ChromaDB collection not initialized")
            return []
        
        # Create query embedding
        query_embedding = self.create_embedding(query)
        if not query_embedding:
            return []
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        count = self.collection.count()
        
        # Get sample to analyze
        sample = self.collection.get(limit=1000)
        
        categories = {}
        sources = {}
        
        for metadata in sample['metadatas']:
            cat = metadata.get('category', 'unknown')
            src = metadata.get('source', 'unknown')
            
            categories[cat] = categories.get(cat, 0) + 1
            sources[src] = sources.get(src, 0) + 1
        
        return {
            'total_chunks': count,
            'categories': categories,
            'unique_documents': len(sources),
            'top_sources': sorted(sources.items(), key=lambda x: -x[1])[:10]
        }


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Mythara Knowledge Base Builder')
    parser.add_argument('--index-all', action='store_true', help='Index all knowledge base documents')
    parser.add_argument('--test-search', type=str, help='Test search with a query')
    parser.add_argument('--stats', action='store_true', help='Show knowledge base statistics')
    parser.add_argument('--rebuild', action='store_true', help='Rebuild entire knowledge base (deletes existing)')
    
    args = parser.parse_args()
    
    # Initialize builder
    kb = KnowledgeBaseBuilder()
    
    # Rebuild
    if args.rebuild:
        print("🔄 Rebuilding knowledge base...")
        if kb.chroma_client:
            kb.chroma_client.delete_collection("mythara_knowledge")
            kb.collection = kb.chroma_client.create_collection(
                name="mythara_knowledge",
                metadata={"description": "Mythara Archive customer-facing documentation"}
            )
        args.index_all = True  # Auto-index after rebuild
    
    # Index
    if args.index_all:
        kb.index_documents()
    
    # Stats
    if args.stats:
        stats = kb.get_stats()
        print("\n📊 Knowledge Base Statistics")
        print("="*50)
        print(f"Total chunks: {stats['total_chunks']}")
        print(f"Unique documents: {stats['unique_documents']}")
        print(f"\nCategories:")
        for cat, count in sorted(stats['categories'].items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count} chunks")
        print(f"\nTop documents:")
        for src, count in stats['top_sources'][:5]:
            print(f"  {src}: {count} chunks")
    
    # Test search
    if args.test_search:
        print(f"\n🔍 Searching: '{args.test_search}'")
        print("="*50)
        
        results = kb.search(args.test_search, n_results=3)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['metadata']['title']}")
            print(f"   Source: {result['metadata']['source']}")
            if result['distance']:
                print(f"   Relevance: {1 - result['distance']:.2%}")
            print(f"\n   {result['text'][:300]}...")
    
    # No args = show help
    if not any([args.index_all, args.test_search, args.stats, args.rebuild]):
        parser.print_help()


if __name__ == '__main__':
    main()
