# How the Team Knowledge Base Q&A Works (For LLM Beginners)

This document explains the core AI concepts behind the **Team Knowledge Base Q&A System**. 
You don't need to be an expert,  we'll break down everything from embeddings to vector databases to LLM prompting.

## What is an LLM?

**LLM** stands for **Large Language Model**. It's an AI trained on massive amounts of text (books, websites, articles). LLMs can understand, generate, and summarise human‑like text. Examples: GPT‑4, Llama, Mixtral (which we use here).

In this app, we use an LLM for **one specific task**: answering questions based **only** on the documents your team uploads. If the answer isn't in those documents, the LLM says “I don't know”, no made‑up facts.

## How does the app find relevant information?

The magic happens in three steps:

### 1. Turning text into numbers: Embeddings

Computers don't understand words directly. We convert text into **vectors** (lists of numbers) using a model called **sentence-transformers/all-MiniLM-L6-v2**.

- Each document chunk (about 500 characters) becomes a **384‑dimensional vector** (a list of 384 numbers).
- Your question also becomes a vector of the same size.

Why do this? Because similar meanings produce similar vectors. For example:

> “Our company holiday policy allows 25 days off per year”  
> and  
> “Annual leave entitlement is 25 days”

will have vectors that are very **close together** mathematically.

### 2. Storing vectors for fast search – ChromaDB

We store all document chunks and their vectors in a database called **ChromaDB**. ChromaDB is specialised for **vector search** – it can find the most similar chunks to your question in milliseconds, even with thousands of pages.

Think of it like a smart filing system: instead of reading every page, you jump directly to the paragraphs that are most relevant to your question.

### 3. Measuring similarity – Cosine Similarity

When you ask a question, the app:
- Converts your question into a vector using the same embedding model.
- Asks ChromaDB: *“Which document chunks are closest to this question vector?”*
- ChromaDB returns the top 3 most similar chunks using **cosine similarity** (a score from 0 to 1, where 1 means identical meaning).

The retrieved chunks become the **context** for the LLM.

## How does the LLM answer without hallucinating?

After retrieving relevant chunks, we build a **prompt** – a carefully written instruction that tells the LLM what to do.

Here’s the exact prompt used in the code:

You are a helpful assistant that answers questions based ONLY on the provided context.
If the answer is not in the context, say "I don't have enough information to answer that."

Context:
[chunk 1 from your document]

[chunk 2 from your document]

[chunk 3 from your document]

Question: How many vacation days do we get?

Answer: 
Because the LLM only sees the context you gave it (no internet, no training data), it has no choice but to answer from those chunks. If the answer isn’t there, it must refuse.

This is how we achieve **“no hallucinations”** – the LLM never invents facts.

## Putting it all together: The RAG pattern

This app follows a popular AI pattern called **RAG** (Retrieval‑Augmented Generation).

| Step | What happens | Why |
|------|--------------|-----|
| **Retrieval** | ChromaDB finds document chunks similar to your question | Find relevant information |
| **Augmentation** | We add the retrieved chunks to a prompt | Give context to the LLM |
| **Generation** | The LLM produces an answer based only on that context | Human‑readable, grounded output |

RAG is powerful because the LLM doesn’t need to know anything about your internal documents, it only answers from what we give it. 
This keeps answers accurate and confidential.

## Why did we choose these specific tools?

| Tool | Purpose | Why not something else? |
|------|---------|--------------------------|
| **sentence-transformers/all-MiniLM-L6-v2** | Embeddings (text → numbers) | Free, runs locally, no API key, good quality/speed balance |
| **ChromaDB** | Vector search | Embedded, persistent, no separate server – perfect for learning |
| **Groq (Mixtral 8x7B)** | LLM for answering | Extremely fast inference, free tier (30 requests/min), no GPU needed |
| **FastAPI** | Backend API | High performance, automatic docs, async support |
| **Streamlit** | User interface | Simplest way to build a Python web app |
| **Docker Compose** | Running everything together | One command to start backend, frontend, and database |

## Try it yourself (no code required)

1. Clone the repo and add your Groq API key (free from console.groq.com).
2. Run `docker-compose up --build`.
3. Open http://localhost:8501.
4. Upload a PDF with your company’s HR policy.
5. Ask: *“How many sick days are allowed?”*
6. The app will retrieve the relevant paragraph and answer **only from that document**.
7. If you ask something not in the document, it will say: *“I don’t have enough information to answer that.”*

## What’s happening behind the scenes?

When you upload a file:
- The backend extracts text (using `pypdf` for PDFs, direct decoding for TXT).
- The text is split into chunks of 500 characters (with 50 characters of overlap so no information falls between chunks).
- Each chunk is embedded and stored in ChromaDB with the filename as metadata.

When you ask a question:
- Your question is embedded with the same model.
- ChromaDB returns the top 3 most similar chunks.
- Those chunks are inserted into the prompt.
- The prompt is sent to Groq’s Mixtral model.
- The answer (plus source filenames) is returned to your browser.

## How we prevent hallucinations – more detail

Hallucinations happen when an LLM guesses an answer because it “wants” to be helpful. Our prompt explicitly forbids guessing. We also:

- **Never** include general knowledge in the prompt – only the retrieved chunks.
- **Do not** give the LLM a chance to chat freely. It’s a one‑shot answer.
- **Show sources** to the user. You can expand the “Sources” section to see exactly which document chunks were used. If the answer seems wrong, you can check the source manually.

**Limitation:** No system is 100% hallucination‑free. With a well‑crafted prompt and good retrieval, it becomes extremely rare. For critical applications (e.g., legal or medical), you can add an extra verification step – for example, ask a second LLM to check if the answer is supported by the retrieved chunks.

## Tech Lead – What to add for production

If you want to turn this prototype into a real product, here are the most important additions (with free tools):

| Priority | Addition | Free solution |
|----------|----------|----------------|
| **High** | Logging (to debug issues) | Python `logging` module with JSON format |
| **High** | Error handling & retries | `tenacity` library (retry on API failures) |
| **High** | API key authentication | `X-API-Key` header in FastAPI |
| **High** | Persistent vector DB (data survives restarts) | Migrate to Pinecone (free tier) |
| **Medium** | Uptime monitoring | UptimeRobot (pings `/health` every 5 min) |
| **Medium** | Rate limiting (Groq allows 30 req/min) | `slowapi` (10 req/min per IP) |
| **Medium** | Cache identical questions | `functools.lru_cache` |
| **Low** | Load testing | Locust or k6 |

## Further learning

- [Embeddings explained visually](https://developers.google.com/machine-learning/crash-course/embeddings/translating-to-a-lower-dimensional-space)
- [What is RAG? (easy video)](https://www.youtube.com/watch?v=T-D1OfcDW1c)
- [ChromaDB tutorial](https://docs.trychroma.com/getting-started)
- [Groq documentation](https://console.groq.com/docs/quickstart)
- [FastAPI for beginners](https://fastapi.tiangolo.com/tutorial/)

## Common questions

**Q: Does the app store my documents anywhere?**  
A: When running locally, everything stays on your computer. When deployed, documents are stored in the vector database (ChromaDB or Pinecone). Choose a trusted provider.

**Q: Can I run this without an internet connection?**  
A: Partially. Embeddings (ChromaDB) work offline. The LLM (Groq) requires internet. You can replace Groq with a local LLM like Ollama, but that’s more advanced.

**Q: How accurate are the answers?**  
A: Very accurate if the answer is explicitly stated in your documents. If the answer requires reasoning across multiple chunks, retrieval may miss some context. You can improve by increasing `top_k` (e.g., 5 chunks) and using a larger LLM.

**Q: Can I use OpenAI instead of Groq?**  
A: Yes. Modify `generate_answer()` in `rag_engine.py` to call OpenAI’s API instead. You’ll need an API key and to adjust the prompt format.

**Q: Why 500‑character chunks?**  
A: It’s a balance between having enough context and keeping chunks precise. You can change this in `rag_engine.py`. Smaller chunks = more precise retrieval but may miss surrounding context. Larger chunks = more context but can include irrelevant text.

**Q: How do I delete a document?**  
A: The current version doesn’t have a delete endpoint. You can delete the ChromaDB collection manually (delete the `chroma_db` folder) and re‑upload all documents. For production, add a `/delete` endpoint that removes by `source` metadata.

---

Happy building! :)