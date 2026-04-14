import os
import hashlib
from typing import List, Tuple
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
import groq

from .config import settings


class RAGEngine:
    def __init__(self):
        # 1. Embedding model (local, free)
        self.embed_model = SentenceTransformer(settings.EMBEDDING_MODEL)

        # 2. ChromaDB client 
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

        # 3. Collection for documents
        self.collection = self.chroma_client.get_or_create_collection(
            name="knowledge_base",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL
            )
        )

        # 4. LLM client (Groq - fast and free)
        self.llm_client = groq.Groq(api_key=settings.GROQ_API_KEY)

        # 5. Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from uploaded PDF."""
        reader = PdfReader(file_bytes)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def add_document(self, filename: str, file_bytes: bytes) -> int:
        """Process and store a document in the vector DB."""
        # Extract text
        if filename.endswith('.pdf'):
            text = self.extract_text_from_pdf(file_bytes)
        else:  # assume .txt
            text = file_bytes.decode('utf-8')

        # Chunk the text
        chunks = self.text_splitter.split_text(text)

        # Generate IDs (hash of chunk content)
        ids = [hashlib.md5(chunk.encode()).hexdigest() for chunk in chunks]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

        # Add to Chroma (embedding happens automatically)
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        return len(chunks)

    def retrieve_relevant_chunks(self, question: str, top_k: int = 3) -> List[Tuple[str, dict]]:
        """Retrieve most similar chunks to the question."""
        results = self.collection.query(
            query_texts=[question],
            n_results=top_k
        )
        # results contains 'documents', 'metadatas', 'distances'
        chunks = []
        if results['documents']:
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                chunks.append((doc, meta))
        return chunks

    def generate_answer(self, question: str, context_chunks: List[Tuple[str, dict]]) -> str:
        """Use LLM to answer based on retrieved chunks."""
        # Build context string
        context = "\n\n---\n\n".join([chunk for chunk, _ in context_chunks])

        # Prompt template (critical for grounded answers)
        prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided context.
If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Answer:"""

        # Call Groq (free, fast)
        response = self.llm_client.chat.completions.create(
            model="mixtral-8x7b-32768",  # good free model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    def answer_question(self, question: str) -> dict:
        """Full RAG pipeline: retrieve + generate."""
        chunks = self.retrieve_relevant_chunks(question)
        if not chunks:
            return {"answer": "No relevant documents found.", "sources": []}
        answer = self.generate_answer(question, chunks)
        sources = list(set([meta["source"] for _, meta in chunks]))
        return {"answer": answer, "sources": sources}