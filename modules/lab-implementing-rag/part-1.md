<h1>
  <span>

  ![alt text](/assets/ga-logo.png)

  </span>
  <span class="subhead"> Part 1 - Prepare Documents and Build a Vector Store</span>
</h1>




## Goal

Load policy documents, split them into chunks, embed them, and build a searchable vector index.

## Before You Start

Make sure you've completed the setup from the README:
- Installed all packages
- Created `.env` file with your OpenAI API key
- Added `load_dotenv()` to the top of your `lab.py` file



## The Big Picture

In this part, you'll convert text documents into a searchable format. Think of it like building a smart search engine:

1. **Load** documents from files
2. **Chunk** them into smaller pieces (paragraphs, not whole documents)
3. **Embed** each chunk (convert text to numbers that capture meaning)
4. **Index** embeddings (store them for fast similarity search)

## Why Chunking Matters

LLMs have token limits, and large documents won't fit in a single prompt. More importantly, smaller chunks improve retrieval precision. When a user asks "What's the approval threshold for expenses?", you want to retrieve just the paragraph about thresholds, not the entire 50-page policy.

**Key Trade-offs:**

- **Chunk too small**: You lose context (e.g., a sentence without its surrounding explanation)
- **Chunk too large**: You dilute relevance (the needle gets lost in the haystack)
- **Overlap**: Ensures important information at chunk boundaries isn't split awkwardly

## Steps

### 1. Load documents
First, let's load all policy documents from a directory.

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import glob

# Load all .txt files from the policies directory
# Using TextLoader directly to avoid dependency on 'unstructured' package
policy_files = glob.glob("data/policies/*.txt")
docs = []
for file_path in policy_files:
    loader = TextLoader(file_path)
    docs.extend(loader.load())

# Split documents into manageable chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,      # ~200 tokens per chunk
    chunk_overlap=120    # 15% overlap to preserve context
)
splits = splitter.split_documents(docs)

print(f"Loaded {len(docs)} documents")
print(f"Split into {len(splits)} chunks")
print("\nSample chunk:")
print(splits[0].page_content)
print(f"\nMetadata: {splits[0].metadata}")
```

**Inspect:** Notice how each chunk retains metadata (like source filename). This becomes your citation trail later!

**Expected output:**
```
Loaded 3 documents
Split into 3 chunks

Sample chunk:
HR-101: Remote Work Policy
...
```

### 2. Embed and index

Now we'll convert text chunks into **vector embeddings** (numerical representations that capture meaning) and store them in a vector database.

**What are embeddings?** They're lists of numbers that represent the semantic meaning of text. Similar meanings → similar numbers. This lets us find relevant text by comparing meanings, not just keywords.

Add this code:

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Create embeddings using OpenAI's embedding model
emb = OpenAIEmbeddings()

# Build a FAISS vector store (local, in-memory)
vs = FAISS.from_documents(splits, emb)

# Create a retriever that returns top 4 most similar chunks
retriever = vs.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

print("Vector store created and ready for retrieval")
```

**What's happening here?**

- Each chunk is converted to a 1536-dimensional vector (OpenAI's embedding size)
- FAISS indexes these vectors for fast similarity search
- When you query, your question is also embedded and compared to all chunks
- The most semantically similar chunks are returned

### 3. Test retrieval

Let's verify that retrieval works. Add this code:

```python
query = "What is the dual approval threshold for PAY-002?"
results = retriever.invoke(query)

print(f"\nRetrieved {len(results)} chunks for: '{query}'\n")
for i, doc in enumerate(results, 1):
    print(f"--- Chunk {i} ---")
    print(doc.page_content[:300])  # First 300 chars
    print(f"Source: {doc.metadata.get('source', 'Unknown')}\n")
```

**Run it!** Execute your `lab.py` file:
```bash
python lab.py
```

You should see the PAY-002 expense policy chunk returned first (highest relevance).

**Discussion Point:** Try different queries. Does it always find the right chunks? What happens if you ask about something not in the documents?

**Checkpoint:** You can run a query and see relevant text chunks returned with their source files.

---
