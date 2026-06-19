## Step 10: Embedding Code Chunks with Metadata

### What did I build?

I created a layer that converts `CodeChunk` objects into:

- an embedding matrix
- a metadata list

The embedding matrix stores numerical vectors.

The metadata list stores source information for each vector.

### Why separate embeddings and metadata?

Vector search libraries such as FAISS mainly work with numerical vectors.

But after FAISS returns a matching vector ID, the system still needs to know:

- which file the chunk came from
- which lines it belongs to
- what the original code was
- what language it is written in

Therefore, embeddings and metadata are stored separately but kept in the same order.

### What is the alignment rule?

The vector at position `i` must match the metadata at position `i`.

Example:

`embeddings[5]` belongs to `metadata[5]`.

This allows the system to map FAISS search results back to original code chunks.

### Why not put metadata inside FAISS?

FAISS is optimized for vector similarity search. It does not act like a full metadata database.

A separate metadata store gives more flexibility for source attribution, filtering and debugging.

### Why use a fake embedding model in tests?

The purpose of the test is to verify chunk-to-embedding pipeline logic, not the transformer model itself.

Using a fake model makes the test:

- fast
- deterministic
- offline
- focused on our code

### Interview question

**Question:** How do you map a retrieved vector back to the original source code?

**Answer:**  
I maintain a metadata list aligned with the embedding matrix. When FAISS returns a vector index, I use the same index to retrieve the source file path, line numbers, language and chunk content from metadata.

### Interview question

**Question:** Why store chunk content inside metadata?

**Answer:**  
The LLM needs the actual retrieved code as context. FAISS only returns vector IDs and scores, so metadata must preserve the original chunk content.

### Interview question

**Question:** What could go wrong if embeddings and metadata order are not aligned?

**Answer:**  
The system may retrieve the correct vector but display or send the wrong source code to the LLM. This would produce incorrect citations and unreliable answers.

### Resume relevance

This step demonstrates:

- vector-to-source mapping
- metadata design
- retrieval traceability
- testable embedding pipeline
- separation between numerical search and source attribution