## Step 11: FAISS Index Save/Load and Per-Repository Vector Storage

### Simple Summary

In this step, we decided how to store FAISS indexes on disk.

Each GitHub repository will have its own separate FAISS index and metadata file.

This is important because every repository has different code, different chunks, and different embeddings.

So we should not mix all repositories into one common FAISS index.

---

## Why Save FAISS Index to Disk?

Creating a FAISS index requires several steps:

```text
Clone repository
↓
Parse files
↓
Create code chunks
↓
Generate embeddings
↓
Build FAISS index
```

This can take time, especially for large repositories.

If we rebuild everything every time the app starts, it will be slow.

So after building the FAISS index once, we save it to disk.

Then next time, we can simply load the saved index.

---

## First Time Flow

When a repository is indexed for the first time:

```text
GitHub repository URL
↓
Clone repository
↓
Parse files
↓
Create chunks
↓
Generate embeddings
↓
Create FAISS index
↓
Save index.faiss
↓
Save metadata.json
```

Example:

```text
vector_store/octocat/Hello-World/index.faiss
vector_store/octocat/Hello-World/metadata.json
```

---

## Next Time Flow

When the same repository is used again:

```text
Check if index.faiss exists
Check if metadata.json exists
↓
If both exist:
    load existing index and metadata
↓
If not:
    rebuild the index
```

This saves time and avoids unnecessary embedding generation.

---

## Why Store One Index Per Repository?

Each repository should have its own FAISS index.

Example structure:

```text
vector_store/
├── octocat/
│   └── Hello-World/
│       ├── index.faiss
│       └── metadata.json
│
├── pallets/
│   └── markupsafe/
│       ├── index.faiss
│       └── metadata.json
│
└── psf/
    └── requests/
        ├── index.faiss
        └── metadata.json
```

This keeps each repository separate.

If a user asks a question about `pallets/markupsafe`, the system should only search inside:

```text
vector_store/pallets/markupsafe/index.faiss
```

It should not return results from another repository like `psf/requests`.

---

## What Problem Happens If All Repos Share One Index?

If all repositories are stored in one common index:

```text
common_index.faiss
```

then a user may ask about one repository, but FAISS may return chunks from another repository.

Example:

```text
User asks about Repo A
↓
FAISS searches all repos
↓
FAISS returns code from Repo B
```

This makes answers confusing and incorrect.

Per-repository indexes avoid this problem.

---

## Difference Between Repo Storage and Vector Storage

There are two separate storage areas.

### 1. Repository Storage

This stores the actual cloned source code.

```text
repo_storage/
└── owner/
    └── repo/
        ├── .git/
        ├── src/
        ├── README.md
        └── other files
```

Example:

```text
repo_storage/octocat/Hello-World/
```

### 2. Vector Storage

This stores the FAISS index and metadata.

```text
vector_store/
└── owner/
    └── repo/
        ├── index.faiss
        └── metadata.json
```

Example:

```text
vector_store/octocat/Hello-World/
```

So the same repository can have two locations:

```text
repo_storage/octocat/Hello-World/
vector_store/octocat/Hello-World/
```

The first one stores actual source code.

The second one stores searchable vector data.

---

## What Is `index.faiss`?

`index.faiss` is the saved FAISS vector index.

It stores numerical vectors created from code chunks.

Example:

```text
Code chunk 0 → vector 0
Code chunk 1 → vector 1
Code chunk 2 → vector 2
```

FAISS uses these vectors to search for the most similar chunks when a user asks a question.

---

## What Is `metadata.json`?

`metadata.json` stores information about each vector.

FAISS only stores vectors and returns vector IDs.

It does not know the original file path or code content.

So metadata is needed.

Example metadata:

```json
[
  {
    "content": "def authenticate_user(...): ...",
    "file_path": "src/auth.py",
    "file_name": "auth.py",
    "language": "python",
    "start_line": 10,
    "end_line": 40,
    "chunk_index": 0
  }
]
```

---

## Why Do We Need Metadata?

FAISS may return:

```text
index = 0
score = 0.89
```

But this only means:

```text
Vector 0 is a good match
```

It does not tell us:

```text
Which file?
Which lines?
What code?
Which language?
```

Metadata tells us:

```text
metadata[0] = src/auth.py, lines 10-40
```

So metadata connects vector search results back to real code.

---

## Very Important Rule: Index and Metadata Must Stay Aligned

The FAISS vector index and metadata list must follow the same order.

Example:

```text
FAISS vector 0 → metadata[0]
FAISS vector 1 → metadata[1]
FAISS vector 2 → metadata[2]
```

If FAISS returns index `2`, then we use:

```text
metadata[2]
```

to find the original source code.

If this order breaks, the system may return the wrong code for a correct vector match.

---

## How Save Works

When we call:

```python
store.save("vector_store/octocat/Hello-World/index.faiss")
```

the system saves the FAISS index to disk.

The save method:

1. converts the input path into a `Path` object
2. creates the parent folder if it does not exist
3. writes the FAISS index file to disk

Conceptually:

```text
FAISS index in memory
↓
write to disk
↓
index.faiss
```

---

## How Load Works

When we call:

```python
store = FaissVectorStore.load("vector_store/octocat/Hello-World/index.faiss")
```

the system loads the saved FAISS index from disk.

The load method:

1. converts the input path into a `Path` object
2. checks if the file exists
3. if the file does not exist, raises `FileNotFoundError`
4. reads the FAISS index from disk
5. creates a `FaissVectorStore` object
6. attaches the loaded FAISS index to that object
7. returns the ready-to-use store

Conceptually:

```text
index.faiss on disk
↓
read from disk
↓
FAISS index in memory
↓
ready for search
```

---

## Do We Check If the Index Exists?

Yes.

Before loading, we check whether the FAISS index file exists.

If it exists, we load it.

If it does not exist, we cannot load it.

In the full pipeline, this check will help us decide:

```text
If index exists:
    load it
else:
    build a new one
```

---

## Should Save Check If the Index Already Exists?

In the current simple version, save can overwrite the existing file.

For MVP, this is acceptable.

Later, we can improve this with options like:

```text
overwrite=True
overwrite=False
versioned indexes
repository commit hash based indexes
```

A production system should be more careful about overwriting existing indexes.

---

## Future Full Pipeline Logic

Later, the system can work like this:

```python
index_path = "vector_store/octocat/Hello-World/index.faiss"
metadata_path = "vector_store/octocat/Hello-World/metadata.json"

if index_path exists and metadata_path exists:
    load index
    load metadata
else:
    clone repository
    parse files
    chunk files
    generate embeddings
    build FAISS index
    save index
    save metadata
```

This makes the system faster for repeated use.

---

## Why Use Owner and Repo Name in Vector Storage?

Repository names are not always unique.

Example:

```text
github.com/user-one/sample
github.com/user-two/sample
```

Both repositories are named:

```text
sample
```

If we store only by repo name:

```text
vector_store/sample/
```

there will be a conflict.

So we store using both owner and repo name:

```text
vector_store/user-one/sample/
vector_store/user-two/sample/
```

This avoids collisions.

---

## Full Storage Design

For a repository:

```text
https://github.com/octocat/Hello-World.git
```

The cloned source code will be stored at:

```text
repo_storage/octocat/Hello-World/
```

The vector index and metadata will be stored at:

```text
vector_store/octocat/Hello-World/
```

Inside vector storage:

```text
vector_store/octocat/Hello-World/
├── index.faiss
└── metadata.json
```

---

## Full Retrieval Flow After Save/Load

```text
User selects repository
↓
System checks vector_store/owner/repo/
↓
If index.faiss and metadata.json exist:
    load them
else:
    build them
↓
User asks a question
↓
Question becomes query embedding
↓
FAISS searches index.faiss
↓
FAISS returns vector IDs and scores
↓
metadata.json maps IDs to source code
↓
Relevant chunks are sent to the LLM
↓
LLM answers with source citations
```

---

# Interview Questions and Answers

## Q1. Why do you save the FAISS index to disk?

I save the FAISS index so that I do not need to recreate embeddings and rebuild the index every time the application starts. This makes repeated searches much faster.

---

## Q2. What is stored inside `index.faiss`?

`index.faiss` stores the embedding vectors. These vectors are created from code chunks and are used for similarity search.

---

## Q3. Does FAISS store metadata like file path and line numbers?

No. FAISS mainly stores vectors. Metadata such as file path, line numbers, language, and chunk content must be stored separately.

---

## Q4. Why do you need `metadata.json`?

`metadata.json` maps each FAISS vector ID back to the original code chunk. Without metadata, FAISS can tell us which vector matched, but not which file or code it came from.

---

## Q5. Why store one FAISS index per repository?

Each repository should be searched separately. If all repositories share one index, a query about one repository may return chunks from another repository. Per-repository indexes keep retrieval scoped and accurate.

---

## Q6. How do you avoid repository name collisions?

I include both the repository owner and repository name in the storage path.

Example:

```text
vector_store/owner/repo/
```

This avoids conflicts when different owners have repositories with the same name.

---

## Q7. What is the difference between `repo_storage` and `vector_store`?

`repo_storage` stores the actual cloned repository files.

`vector_store` stores the FAISS index and metadata used for semantic search.

---

## Q8. What happens if the FAISS index already exists?

If the index already exists, the system can load it from disk instead of rebuilding it. This saves time and computation.

---

## Q9. What happens if the FAISS index does not exist?

If the index file does not exist, the system cannot load it. The repository must be parsed, chunked, embedded, and indexed again.

---

## Q10. How does the `save()` method work?

The `save()` method creates the parent directory if needed and writes the FAISS index to disk using FAISS’s write function.

---

## Q11. How does the `load()` method work?

The `load()` method checks if the index file exists. If it exists, it reads the FAISS index from disk, wraps it inside a `FaissVectorStore` object, and returns it.

---

## Q12. Why check if the index file exists before loading?

Because loading a missing file would fail. Checking first gives a clear error and also helps the pipeline decide whether to load an existing index or rebuild it.

---

## Q13. Should saving overwrite an existing index?

In the MVP version, saving can overwrite the existing index. In a production version, we may add safer options like overwrite flags, versioning, or commit-based index paths.

---

## Q14. Why must FAISS index and metadata stay aligned?

FAISS returns vector IDs. The metadata list uses those IDs as positions. If vector ID `5` is returned, `metadata[5]` must describe that same vector. If alignment breaks, the system may show wrong code.

---

## Q15. How do you recover the original source code after FAISS search?

FAISS returns vector indices. I use those indices to look up metadata and recover file path, line numbers, language, and chunk content.

---

## Q16. Why not store all repositories in one global FAISS index?

A global index can mix results from unrelated repositories. Per-repository indexes keep search results focused on the selected repository.

---

## Q17. How would you support cross-repository search later?

I could either search multiple per-repository indexes and merge results, or build a global index with repository metadata filters. For the MVP, per-repository indexes are simpler and safer.

---

## Q18. What is a limitation of this approach?

The system must manage many small indexes if many repositories are indexed. Later, we may need cleanup policies, versioning, repository update detection, and storage management.

---

## Q19. How would you know if an index is outdated?

A future version can store the Git commit hash used during indexing. If the repository HEAD commit changes, the index can be marked outdated and rebuilt.

---

## Q20. What is the resume value of this design?

This design shows understanding of vector persistence, metadata mapping, repository isolation, caching, and scalable retrieval architecture.
