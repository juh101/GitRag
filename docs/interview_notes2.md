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

## Step 11: FAISS Vector Store

### Simple Summary

In this step, I created a FAISS vector store.

The job of this component is to store embedding vectors and search the most similar vectors for a user query.

Before this step, each code chunk was converted into one embedding vector.

Now we need a way to search those vectors quickly.

FAISS helps with that.

---

## Why Do We Need FAISS?

In a real repository, there can be thousands of code chunks.

Example:

```text
Chunk 0 → vector
Chunk 1 → vector
Chunk 2 → vector
...
Chunk 50000 → vector
```

When a user asks a question, the question is also converted into a vector.

Then we need to find which chunk vectors are closest to the query vector.

Doing this manually for thousands of vectors can become slow.

FAISS is used to perform fast vector similarity search.

---

## What Does FAISS Store?

FAISS stores numerical vectors.

It does not naturally store full source information like:

* file path
* line numbers
* original code content
* language
* repository name

So FAISS stores vectors, and a separate metadata store maps vector IDs back to the original code chunks.

Example:

```text
FAISS vector ID 5
```

Metadata tells us:

```text
ID 5 = src/auth/login.py, lines 10-40
```

---

## Important Idea: Vector and Metadata Alignment

The vector and metadata must stay in the same order.

Example:

```text
embeddings[0] → metadata[0]
embeddings[1] → metadata[1]
embeddings[2] → metadata[2]
```

If FAISS returns index `2`, we use `metadata[2]` to get the original file path, line numbers, and code.

This alignment is very important.

If this order breaks, the system may retrieve the correct vector but show the wrong code.

---

## Code Explanation

### Imports

```python
from pathlib import Path

import faiss
import numpy as np
```

`Path` is used for saving and loading FAISS index files.

`faiss` is the vector search library.

`numpy` is used because embeddings are stored as NumPy arrays.

---

## Class: `FaissVectorStore`

```python
class FaissVectorStore:
```

This class is a wrapper around FAISS.

Instead of using FAISS directly everywhere, the project uses this class.

This makes the code cleaner and easier to test.

The class supports:

* creating an index
* adding embeddings
* searching nearest vectors
* saving the index
* loading the index
* counting stored vectors

---

## Constructor

```python
def __init__(self, dimension: int) -> None:
    if dimension <= 0:
        raise ValueError("Vector dimension must be greater than zero.")

    self.dimension = dimension
    self.index = faiss.IndexFlatIP(dimension)
```

The constructor creates a FAISS index.

`dimension` means how many numbers are present in one vector.

Example:

```text
[0.1, 0.2, 0.3]
```

This vector has dimension 3.

The real embedding model usually creates 384-dimensional vectors.

So in real use:

```python
store = FaissVectorStore(dimension=384)
```

---

## Why Validate Dimension?

A vector dimension cannot be zero or negative.

Invalid:

```python
FaissVectorStore(dimension=0)
```

Correct:

```python
FaissVectorStore(dimension=384)
```

Validation prevents incorrect FAISS index creation.

---

## What Is `IndexFlatIP`?

```python
self.index = faiss.IndexFlatIP(dimension)
```

`IndexFlatIP` is a FAISS index type.

It means:

```text
Flat = exact search
IP = inner product
```

I used `IndexFlatIP` because the embeddings are normalized.

With normalized embeddings, inner product behaves like cosine similarity.

This allows semantic similarity search.

Simple explanation:

```text
Normalized vectors + Inner Product ≈ Cosine Similarity
```

---

## `add_embeddings()`

```python
def add_embeddings(self, embeddings: np.ndarray) -> None:
```

This method adds embedding vectors to the FAISS index.

Input example:

```python
embeddings = np.array([
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
])
```

This means:

```text
2 vectors
3 dimensions each
```

Shape:

```text
(2, 3)
```

---

## Why Must Embeddings Be 2D?

FAISS expects embeddings in matrix form.

Correct:

```text
(number_of_vectors, vector_dimension)
```

Example:

```text
(100, 384)
```

This means:

```text
100 vectors
384 numbers in each vector
```

A single vector like this is 1D:

```text
(384,)
```

But FAISS expects:

```text
(1, 384)
```

---

## Dimension Check

```python
if embeddings.shape[1] != self.dimension:
```

This ensures the vectors match the FAISS index dimension.

If the index expects 384-dimensional vectors, every added vector must also have 384 values.

This prevents incorrect indexing.

---

## Why Convert to `float32`?

```python
if embeddings.dtype != np.float32:
    embeddings = embeddings.astype(np.float32)
```

FAISS expects vectors in `float32`.

`float32` also uses less memory than `float64`.

This matters when storing many embeddings.

---

## Adding Vectors

```python
self.index.add(embeddings)
```

This adds the vectors to the FAISS index.

FAISS automatically gives each vector an internal index.

Example:

```text
First vector  → ID 0
Second vector → ID 1
Third vector  → ID 2
```

These IDs are later used to look up metadata.

---

## `search()`

```python
def search(
    self,
    query_embedding: np.ndarray,
    top_k: int = 5,
) -> tuple[np.ndarray, np.ndarray]:
```

This method searches the FAISS index for the closest vectors to the query vector.

`top_k` means how many results we want.

Example:

```python
scores, indices = store.search(query_embedding, top_k=5)
```

This returns:

* similarity scores
* vector indices

---

## What Are Scores and Indices?

Example result:

```text
scores = [[0.91, 0.84, 0.77]]
indices = [[4, 2, 9]]
```

This means:

```text
Best match = vector 4, score 0.91
Second match = vector 2, score 0.84
Third match = vector 9, score 0.77
```

Then the system uses:

```text
metadata[4]
metadata[2]
metadata[9]
```

to recover the original code chunks.

---

## Why Reshape Query Embedding?

```python
if query_embedding.ndim == 1:
    query_embedding = query_embedding.reshape(1, -1)
```

A single query vector may have shape:

```text
(384,)
```

FAISS expects 2D input:

```text
(1, 384)
```

So the code reshapes it before searching.

---

## `save()`

```python
def save(self, path: str | Path) -> None:
```

This method saves the FAISS index to disk.

Example:

```python
store.save("vector_store/index.faiss")
```

Saving is important because embedding generation can take time.

Instead of rebuilding the index every time, we can save it once and load it later.

---

## `load()`

```python
@classmethod
def load(cls, path: str | Path) -> "FaissVectorStore":
```

This method loads a saved FAISS index from disk.

Example:

```python
store = FaissVectorStore.load("vector_store/index.faiss")
```

It reads the FAISS index file and returns a ready-to-use `FaissVectorStore` object.

---

## Why Use `@classmethod` for Load?

`load()` creates a new object from a saved file.

We call it on the class directly:

```python
FaissVectorStore.load(path)
```

not on an existing object.

That is why `@classmethod` is used.

---

## `count()`

```python
def count(self) -> int:
    return self.index.ntotal
```

This method returns how many vectors are stored in the FAISS index.

Example:

```python
store.count()
```

If output is:

```text
100
```

it means 100 vectors are stored.

---

## Full Flow

```text
Code chunks
    ↓
Embeddings
    ↓
FAISS index
    ↓
User query
    ↓
Query embedding
    ↓
FAISS search
    ↓
Vector IDs and scores
    ↓
Metadata lookup
    ↓
Original code chunks
```

---

## Why Save Metadata Separately?

FAISS only returns vector IDs and scores.

It does not return original code content or file paths.

So metadata must be stored separately.

Example:

```text
FAISS returns index 7
```

Metadata tells us:

```text
index 7 = src/auth.py, lines 20-50
```

---

## Interview Questions and Answers

### Q1. What did you build in the FAISS vector store step?

I built a wrapper around FAISS that can store embedding vectors, search nearest vectors, save the index to disk, load the index from disk, and count stored vectors.

---

### Q2. Why do we need FAISS?

We need FAISS to search similar vectors efficiently. After code chunks and queries are converted into embeddings, FAISS helps retrieve the most relevant chunks quickly.

---

### Q3. What does FAISS store?

FAISS stores numerical vectors. It does not store rich metadata like file paths, line numbers, or original code content.

---

### Q4. What does FAISS return after a search?

FAISS returns similarity scores and vector indices. The indices are used to look up metadata and recover the original code chunks.

---

### Q5. Why is metadata stored separately?

FAISS is optimized for vector search, not metadata management. A separate metadata store maps vector IDs back to file paths, line numbers, language, and chunk content.

---

### Q6. Why is vector-metadata alignment important?

If FAISS returns vector index 5, then `metadata[5]` must describe that same vector. If alignment breaks, the system may return the wrong source code.

---

### Q7. What is vector dimension?

Vector dimension is the number of values in each embedding vector. For example, a 384-dimensional vector has 384 numbers.

---

### Q8. Why does FAISS need the vector dimension during index creation?

FAISS indexes are created for a fixed vector size. Every vector added to the index must have the same dimension.

---

### Q9. Why did you use `IndexFlatIP`?

I used `IndexFlatIP` because it performs inner product search. Since my embeddings are normalized, inner product behaves like cosine similarity.

---

### Q10. What does `Flat` mean in `IndexFlatIP`?

`Flat` means exact search. It compares the query against all stored vectors. It is simple and reliable for an MVP.

---

### Q11. What does `IP` mean in `IndexFlatIP`?

`IP` means inner product. It measures similarity between vectors.

---

### Q12. Why convert vectors to `float32`?

FAISS expects `float32` vectors. `float32` also uses less memory than `float64`.

---

### Q13. Why validate embedding dimensions before adding vectors?

Dimension validation prevents adding incompatible vectors to the index. If the index expects 384-dimensional vectors, all added vectors must also have 384 dimensions.

---

### Q14. Why reshape the query vector?

A single query embedding may be a 1D array like `(384,)`, but FAISS expects 2D input like `(1, 384)`. Reshaping makes it compatible.

---

### Q15. Why save the FAISS index?

Saving the index allows reuse without regenerating embeddings every time. This saves time and computation.

---

### Q16. What is the difference between FAISS index and metadata store?

The FAISS index stores vectors and performs similarity search. The metadata store stores source information such as file path, line numbers, language, and content.

---

### Q17. How do you recover the original code after FAISS search?

FAISS returns vector indices. I use those indices to access the metadata list and recover the original code chunk.

---

### Q18. Is FAISS a full vector database?

Not exactly. FAISS is mainly a vector similarity search library. It does not provide full database features like rich metadata filtering or persistence management by default.

---

### Q19. What is a limitation of `IndexFlatIP`?

It performs exact search by comparing against all vectors. This is simple and accurate, but for very large datasets, approximate indexes may be faster.

---

### Q20. How can this be improved later?

Later improvements can include:

* approximate FAISS indexes
* metadata filtering
* hybrid retrieval
* reranking
* persistent metadata storage
* incremental indexing
* repository-wise index separation

## Step 12: Metadata Store

### What did I build?

I created a metadata store that saves and loads chunk metadata using JSON files.

Each FAISS vector needs matching metadata so the system can map vector search results back to original source code.

---

### Why is metadata needed?

FAISS stores and searches numerical vectors.

It does not know:

- source file path
- line numbers
- programming language
- original chunk content

So metadata is stored separately.

---

### What does metadata contain?

Each metadata item contains information such as:

- chunk content
- file path
- file name
- language
- start line
- end line
- chunk index

Example:

```json
{
  "content": "def authenticate_user(...): ...",
  "file_path": "src/auth.py",
  "file_name": "auth.py",
  "language": "python",
  "start_line": 10,
  "end_line": 40,
  "chunk_index": 0
}