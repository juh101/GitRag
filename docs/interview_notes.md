# GitHub Repository RAG — Interview Notes

## Step 1: CodeDocument Data Model

### What did I build?

I created a typed `CodeDocument` data model using Python's `dataclass`.

It represents one source-code or documentation file extracted from a GitHub repository.

The model stores:

- file content
- relative file path
- file name
- file extension
- programming language
- file size in bytes

---

### Why did I create a structured data model?

The RAG pipeline needs more than raw text.

Along with the code content, downstream components need metadata such as:

- where the code came from
- which programming language it uses
- its file type
- its source path
- its size

This metadata is later useful for:

- chunking
- language-specific parsing
- metadata filtering
- source citations
- retrieval debugging
- answer generation

---

### Why use a dataclass instead of a dictionary?

A dictionary would work for a basic prototype, but a dataclass provides:

- a predictable schema
- type hints
- readable object output
- easier testing
- IDE autocomplete
- fewer errors caused by misspelled dictionary keys

The dataclass creates a clear contract between ingestion and downstream pipeline components.

---

### Why store both file_name and file_path?

A repository may contain multiple files with the same name.

Example:

- frontend/auth/login.py
- backend/auth/login.py
- tests/auth/login.py

The file name is useful for display, while the relative file path uniquely identifies the file.

---

### Why store file size?

Some repositories contain very large or generated files such as:

- package-lock.json
- minified JavaScript files
- compiled assets
- generated code
- large datasets

File-size metadata allows the ingestion pipeline to skip oversized files that may waste memory, embedding cost and retrieval space.

---

### Important interview answer

Question: Why did you not pass raw text directly to the embedding model?

Answer:

I wanted to preserve source metadata throughout the pipeline. Raw text alone would make it difficult to provide citations, identify the source file, filter by language or debug retrieval results. Therefore, I created a structured document model containing both content and metadata.

---

### Software engineering concepts demonstrated

- data modelling
- typed interfaces
- separation of concerns
- modular pipeline design
- metadata management
- maintainability

## Step 2: Repository File Filtering

### What did I build?

I created a file-filtering module that decides which repository files and directories should be processed during ingestion.

The module filters based on:

- ignored directory names
- supported file extensions
- maximum file size
- whether the path is an actual file

---

### Why is filtering required?

GitHub repositories often contain large amounts of irrelevant or generated content such as:

- dependency folders
- version-control metadata
- build output
- caches
- compiled files
- minified assets

Indexing these files would increase parsing time, embedding generation, vector-storage usage and retrieval noise.

Filtering improves both system performance and retrieval quality.

---

### Why use an allowlist of extensions?

An allowlist makes ingestion predictable and reduces the risk of reading binary or unsupported files.

A blocklist could miss unknown binary formats, while an allowlist processes only file types that the system explicitly understands.

The trade-off is that uncommon but useful file types may need to be added later.

---

### Why use a set for ignored directories and extensions?

Set membership checks have average O(1) lookup complexity.

Since directory and extension checks occur repeatedly while traversing repositories, sets provide efficient and readable membership testing.

---

### Why use pathlib?

`pathlib` provides object-oriented, readable and cross-platform file-system operations.

It avoids manually handling Windows and Linux path separators and provides convenient methods such as:

- suffix
- name
- is_file
- stat
- parent

---

### Why skip large files?

Very large repository files are often generated, bundled or data-heavy.

They can:

- slow indexing
- consume excessive memory
- produce too many chunks
- reduce retrieval precision
- increase embedding cost

The current file-size limit is a configurable heuristic, not a universal rule.

---

### Important trade-off

Ignoring directories improves speed and relevance, but an aggressively filtered repository may lose useful information.

For example, `.github/workflows` may be useful for deployment or CI/CD questions.

A future version can support query-aware or configurable filtering.

---

### Interview question

Question: How did you prevent irrelevant repository files from entering the RAG index?

Answer:

I implemented an ingestion filter using directory pruning, extension allowlisting and file-size limits. This excluded dependencies, build artifacts, caches and unsupported files before parsing and embedding.

---

### Interview question

Question: Why not ingest the entire repository?

Answer:

More indexed data does not always mean better retrieval. Generated and dependency files add noise, increase storage and can rank above relevant source files. Selective ingestion improves both efficiency and answer quality.

---

### Resume relevance

This component demonstrates:

- file-system traversal design
- data filtering
- complexity awareness
- preprocessing for information retrieval
- testable modular architecture

## Step 3: Repository Parser

### What did I build?

I created a repository parser that recursively traverses a cloned repository, removes ignored directories, reads supported text files and converts each valid file into a structured `CodeDocument`.

### Why use os.walk()?

`os.walk()` recursively traverses a directory tree and returns:

- current root path
- child directories
- files in the current directory

It is suitable for repository ingestion because it allows directory pruning before deeper traversal.

### What is directory pruning?

Directory pruning means removing unwanted directory names from the mutable `directories` list returned by `os.walk()`.

This prevents `os.walk()` from entering folders such as:

- node_modules
- .git
- venv
- build
- dist

This is more efficient than entering those directories and skipping their files afterward.

### Why return a list of CodeDocument objects?

The parser acts as a contract between filesystem ingestion and downstream chunking.

Each document preserves:

- source content
- relative path
- filename
- extension
- language
- file size

This metadata is required later for citations, filtering and retrieval debugging.

### Why store relative paths instead of absolute paths?

Absolute paths depend on the machine where the repository was indexed.

Relative paths are:

- portable
- cleaner for citations
- repository-specific
- safe to display to users

### Why catch UnicodeDecodeError?

Not every file with a supported-looking extension is guaranteed to be valid UTF-8 text.

Catching decoding errors prevents one problematic file from crashing the complete repository ingestion process.

### Interview question

**Question:** How did you efficiently ignore dependency directories?

**Answer:**  
I pruned the mutable directory list produced by `os.walk()`. This prevented traversal into ignored directories entirely instead of discovering and rejecting every file inside them.

### Interview question

**Question:** What happens if one file cannot be read?

**Answer:**  
The parser uses fault isolation. A decoding or operating-system error causes that individual file to be skipped, while ingestion continues for the remaining repository.

### Trade-off

Skipping unreadable files keeps indexing robust, but silent skipping may hide useful information.

A production version should collect ingestion warnings and skipped-file statistics instead of only returning documents.

### Resume relevance

This component demonstrates:

- recursive filesystem traversal
- directory pruning
- defensive file reading
- metadata extraction
- typed data pipelines
- fault-tolerant ingestion

## Step 4: Git Repository Cloning

### What did I build?

I created a repository acquisition module that clones a Git repository into local storage using GitPython.

The module:

- extracts the repository name from the URL
- creates the storage directory
- avoids unnecessary duplicate cloning
- detects conflicting non-Git directories
- converts Git-specific failures into application-level errors
- returns a resolved local repository path

### Why clone the repository locally?

The later RAG stages need filesystem access to:

- traverse directories
- inspect file metadata
- read source files
- parse code
- build dependency information

Cloning provides a stable local snapshot and avoids making a separate GitHub API request for every file.

### Why not use the GitHub API?

The GitHub API is useful for remote metadata and selective file access, but cloning is simpler for full-repository indexing.

Cloning provides:

- native filesystem access
- fewer API-rate-limit concerns
- complete repository structure
- compatibility with Git operations
- easier parsing

The trade-off is additional local disk usage.

### Why check for the .git directory?

A destination folder may exist without being a valid cloned repository.

Checking for `.git` helps distinguish between:

- an existing Git repository that can be reused
- an unrelated directory that should not be overwritten

### Why wrap GitCommandError?

GitPython exposes implementation-specific exceptions.

The ingestion layer converts them into a clearer application-level `RuntimeError` while preserving the original exception chain for debugging.

### Why mock Repo.clone_from in unit tests?

Real network operations would make tests slow and nondeterministic.

Mocking allows the unit test to verify:

- correct function calls
- destination-path construction
- error handling

without depending on GitHub or internet availability.

### Interview question

**Question:** Why did you choose cloning instead of reading files through GitHub APIs?

**Answer:**  
I wanted complete and repeatable filesystem access for parsing. Cloning avoids per-file API calls and makes recursive traversal, metadata extraction and future AST analysis straightforward. The trade-off is local storage usage, which can later be managed with cleanup and caching policies.

### Interview question

**Question:** How did you make cloning idempotent?

**Answer:**  
Before cloning, I derive the destination path and check whether it already contains a `.git` directory. If it does, I reuse the repository instead of cloning it again.

### Interview question

**Question:** What is idempotency?

**Answer:**  
An idempotent operation can be repeated without causing unintended additional effects. In this case, repeatedly requesting the same repository does not create duplicate clones.

### Resume relevance

This component demonstrates:

- Git automation
- filesystem management
- URL parsing
- idempotent operations
- exception handling
- dependency mocking

## Destination Path Handling During Repository Cloning

### What is the destination path?

The destination path is the local filesystem location where a remote Git repository is cloned.

For example:

GitHub URL:

`https://github.com/psf/requests.git`

Local destination:

`repo_storage/requests`

### How is the destination constructed?

The clone module:

1. selects a base storage directory
2. extracts the repository name from the URL
3. joins the base directory and repository name

Conceptually:

`destination_path = storage_directory / repository_name`

### Why check whether the destination already exists?

If a valid Git repository already exists at the destination, the system reuses it instead of cloning it again.

This avoids:

- duplicate repositories
- unnecessary network calls
- extra storage usage

If the folder exists but does not contain `.git`, the operation raises an error instead of overwriting unknown user data.

### Why return an absolute path?

An absolute path gives downstream components an unambiguous filesystem location.

The parser can then traverse the cloned repository without depending on the caller's current working directory.

### What is the current limitation?

The current destination uses only the repository name.

Repositories from different owners may share the same name and therefore cause a path collision.

A production version should include both repository owner and repository name in the storage path.

### Interview question

**Question:** How did you avoid overwriting an existing directory?

**Answer:**  
Before cloning, I checked whether the destination path already existed. If it contained a `.git` directory, I reused it as an existing clone. Otherwise, I raised a `FileExistsError` rather than deleting or overwriting unknown data.

### Interview question

**Question:** Why not generate a random destination folder?

**Answer:**  
A deterministic path makes repository reuse and caching easier. However, it must include enough repository identity, such as owner and repository name, to avoid collisions.

## Step 5: Repository Ingestion Orchestration

### What did I build?

I created an ingestion orchestration layer that connects repository cloning with repository parsing.

The ingestion function accepts a GitHub repository URL and returns a list of structured `CodeDocument` objects.

### Pipeline

GitHub URL  
→ clone or reuse repository  
→ obtain local repository path  
→ parse supported files  
→ return structured documents

### Why keep orchestration separate?

Cloning and parsing are independent components.

The orchestration layer coordinates them without mixing their responsibilities.

This improves:

- separation of concerns
- testability
- maintainability
- reusability
- future API integration

### Why return documents instead of printing everything?

Returning documents allows the next pipeline component, such as chunking, to consume the result programmatically.

Printing is only used for CLI feedback.

### Why use dependency mocking in the test?

The orchestration test should validate coordination logic rather than GitHub connectivity.

Mocking makes the test:

- fast
- deterministic
- offline
- focused on one responsibility

### Interview question

**Question:** What is an orchestration layer?

**Answer:**  
An orchestration layer coordinates multiple lower-level components to complete a workflow. In this project, it connects repository acquisition and parsing while keeping their internal logic separate.

### Interview question

**Question:** Why not put parsing inside clone_repository?

**Answer:**  
Cloning and parsing have different responsibilities. A cloned repository may be parsed multiple times, and the parser may also process repositories obtained through other means. Keeping them separate improves reuse and testing.

### Interview question

**Question:** Is this a unit test or integration test?

**Answer:**  
The mocked orchestration test is a unit test because dependencies are isolated. Running the CLI against a real GitHub repository is an integration test because it exercises Git, filesystem operations and parsing together.

### Resume relevance

This step demonstrates:

- modular pipeline design
- orchestration
- CLI development
- dependency injection concepts
- unit testing with mocks
- separation of concerns

from dataclasses import dataclass


@dataclass
class CodeChunk:
    """
    Represents a smaller retrievable section of a repository file.
    """

    content: str
    file_path: str
    file_name: str
    language: str
    start_line: int
    end_line: int
    chunk_index: int

    ## Step 7: Line-Based Code Chunking

### What did I build?

I implemented a line-based chunking module that converts complete `CodeDocument` objects into smaller overlapping `CodeChunk` objects.

Each chunk preserves:

- source file path
- file name
- programming language
- starting line
- ending line
- chunk position

### Why is chunking required?

A source file may contain several unrelated classes, functions and configuration sections.

Embedding the entire file into one vector can dilute the meaning of individual code regions. Smaller chunks create more focused vector representations and improve retrieval precision.

### Why start with line-based chunking?

Line-based chunking is:

- simple to implement
- deterministic
- language-independent
- easy to test
- a useful baseline

It provides a working retrieval pipeline before introducing more complex AST-based chunking.

### Why use overlap?

Overlap preserves context around chunk boundaries.

Without overlap, a function or logical block may be split between two chunks. Repeating a small number of lines in adjacent chunks reduces context loss.

### What is the trade-off of overlap?

Higher overlap improves context preservation but creates more duplicate content, more embeddings and a larger vector index.

### Why validate chunk size and overlap?

Invalid values can create zero or negative step sizes, causing incorrect iteration or runtime failures.

The module requires:

- chunk size greater than zero
- overlap greater than or equal to zero
- overlap smaller than chunk size

### Interview question

**Question:** Why did you choose line-based chunking instead of token-based chunking?

**Answer:**  
I started with line-based chunking because source code is naturally organized by lines and line numbers are needed for citations. It also provides a simple and explainable baseline. A later version can add token limits to ensure compatibility with embedding and LLM context windows.

### Interview question

**Question:** Why not directly start with AST-based chunking?

**Answer:**  
AST chunking gives better semantic boundaries, but it adds language-specific complexity. I first established a deterministic baseline, which allows me to measure whether AST-based chunking actually improves retrieval quality.

### Interview question

**Question:** How did you preserve source traceability?

**Answer:**  
Each chunk retains the original relative file path, language and exact start and end line numbers. This allows retrieved chunks to be mapped back to their source.

### Resume relevance

This component demonstrates:

- text preprocessing
- sliding-window algorithms
- metadata preservation
- configurable retrieval pipelines
- validation and edge-case handling
- baseline-first ML system design

## Step 8: Connecting Ingestion with Chunking

### What did I build?

I extended the repository ingestion pipeline so that parsed `CodeDocument` objects are immediately converted into retrievable `CodeChunk` objects.

The pipeline now performs:

GitHub URL  
→ repository clone  
→ repository parsing  
→ file filtering  
→ document creation  
→ overlapping chunk creation

### What are the data types between stages?

The pipeline uses clear typed boundaries:

- repository URL: `str`
- cloned repository location: `Path`
- parsed files: `list[CodeDocument]`
- retrievable sections: `list[CodeChunk]`

These contracts make the pipeline easier to understand, test and extend.

### Why return both documents and chunks?

Documents are useful for repository-level statistics and debugging.

Chunks are the units that will later be embedded and retrieved.

Returning both allows the application to inspect ingestion results without losing file-level information.

### Why avoid chunking when no documents are found?

Calling later pipeline stages with empty data is unnecessary.

The orchestration layer exits early and returns empty collections, preventing wasted computation and simplifying downstream behaviour.

### What is orchestration?

Orchestration is the coordination of multiple independent components into one workflow.

The orchestration layer does not implement cloning, parsing or chunking itself. It calls those components in the required order and transfers their outputs between stages.

### Interview question

**Question:** What is the data flow in your ingestion pipeline?

**Answer:**  
The system accepts a repository URL, clones it to a deterministic local path, parses supported files into typed `CodeDocument` objects and then converts those documents into overlapping `CodeChunk` objects with source metadata and line boundaries.

### Interview question

**Question:** Why keep CodeDocument and CodeChunk as separate models?

**Answer:**  
A document represents the complete source file and belongs to the ingestion layer. A chunk represents the smaller unit that will be embedded and retrieved. Keeping them separate creates a clear transformation boundary and preserves file-level as well as chunk-level metadata.

### Interview question

**Question:** Are chunks persisted at this stage?

**Answer:**  
No. At this stage, documents and chunks exist only in application memory. Persistence is introduced later when embeddings are stored in FAISS and chunk metadata is stored alongside the vector index.

### Resume relevance

This step demonstrates:

- typed data pipelines
- multi-stage orchestration
- integration testing with mocks
- early-return patterns
- memory versus persistence awareness
- modular retrieval-system architecture

## Embeddings, Normalization, and FAISS

### Simple Summary

In this project, embeddings are used to convert code chunks and user questions into numerical vectors.

A vector is just a list of numbers that represents the meaning of some text or code.

For example:

```text
"verify JWT token"
```

can be converted into a vector like:

```text
[0.12, -0.45, 0.88, ...]
```

The exact numbers are not important to us directly. What matters is that similar meanings should produce similar vectors.

For example:

```text
"verify JWT token"
"decode authentication token"
```

should have similar vectors.

But:

```text
"calculate shopping cart total"
```

should have a different vector.

This helps our RAG system find relevant code even when the user question and the code do not use the exact same words.

---

### Why Do We Need Embeddings?

Keyword search only works well when exact words match.

Example:

User asks:

```text
Where is login checked?
```

But the code may contain:

```python
def authenticate_user():
    ...
```

The word `login` may not be present, but the meaning is related.

Embeddings help the system understand semantic similarity.

So instead of only matching exact words, the system can match meaning.

---

### What Happens in the Embedding Step?

The pipeline becomes:

```text
CodeChunk
    ↓
Embedding model
    ↓
Vector
```

Each code chunk becomes one vector.

The user question also becomes one vector.

Then we compare the query vector with all chunk vectors.

The closest vectors represent the most relevant code chunks.

---

### What Is Normalization?

Vectors have two main properties:

1. Direction
2. Length

In semantic search, direction is more important because it represents meaning.

Normalization makes all vectors have the same length.

This allows fair comparison between vectors.

After normalization, we mainly compare vector direction instead of vector size.

---

### Why Normalize Embeddings?

I normalize embeddings so that similarity comparison becomes more stable.

With normalized vectors, inner product search behaves like cosine similarity.

This is useful because FAISS can efficiently search using inner product.

Simple explanation:

```text
Normalization = make all vectors the same length
Cosine similarity = compare vector direction
Direction = meaning
```

---

### What Is Cosine Similarity?

Cosine similarity measures how similar two vector directions are.

If two vectors point in almost the same direction, their meaning is considered similar.

Example:

```text
"verify JWT token"
"decode authentication token"
```

These should have high cosine similarity.

But:

```text
"verify JWT token"
"calculate cart total"
```

These should have low cosine similarity.

---

### What Is FAISS?

FAISS stands for Facebook AI Similarity Search.

In this project, FAISS is used to quickly search through many embedding vectors and find the closest ones to a user query.

If we have 50,000 code chunks, we do not want to manually compare the query with every chunk slowly.

FAISS helps us find the top matching vectors efficiently.

---

### Is FAISS a Full Database?

FAISS is not a full traditional database like PostgreSQL.

FAISS mainly stores and searches vectors.

It does not naturally store all rich metadata like:

* file path
* line number
* code content
* language
* repository name

So we need two things:

```text
1. FAISS index
   Stores vectors

2. Metadata store
   Stores chunk details
```

Example:

```text
FAISS returns:
ID = 42
Score = 0.87
```

Then metadata tells us:

```text
ID 42 means:
src/auth/login.py
lines 20-60
content: authentication code
```

---

### Why Use the Same Embedding Model for Code Chunks and Queries?

The code chunks and user questions must be converted into vectors in the same vector space.

If different models are used, the vectors may not be comparable.

So the same embedding model should be used for:

* document chunks
* user queries

---

### Why Use `all-MiniLM-L6-v2`?

I used `all-MiniLM-L6-v2` as the initial embedding model because it is:

* free
* lightweight
* fast
* easy to run locally
* good enough for a first baseline

It may not be the best model for source code, but it is useful for building and understanding the full retrieval pipeline first.

Later, I can compare it with code-specific embedding models.

---

### Why Wrap SentenceTransformer in Our Own Class?

Instead of using `SentenceTransformer` directly everywhere, I created an `EmbeddingModel` wrapper.

This is useful because:

* model loading stays in one place
* model replacement becomes easier
* batching can be added later
* caching can be added later
* testing becomes easier
* the rest of the project does not depend directly on one external library

This is a good software engineering practice.

---

### Final Flow

The embedding and retrieval flow is:

```text
Code chunks
    ↓
Create chunk embeddings
    ↓
Store embeddings in FAISS
    ↓
User asks a question
    ↓
Create query embedding
    ↓
Search nearest vectors in FAISS
    ↓
Get matching chunk IDs
    ↓
Use metadata to recover file path, line numbers, and code
    ↓
Send relevant context to LLM
```

---

## Interview Questions and Answers

### Q1. What are embeddings?

Embeddings are dense numerical representations of text or code. They convert meaning into vectors so that similar texts are close to each other in vector space.

---

### Q2. Why do we need embeddings in this project?

We need embeddings because user questions and source code may use different words for the same concept. Embeddings allow semantic search, so the system can find related code even without exact keyword matches.

---

### Q3. Why not only use keyword search?

Keyword search is good for exact terms like `JWT`, `Stripe`, or `login.py`, but it can fail when the query and code use different vocabulary. Embeddings improve semantic matching.

---

### Q4. What is semantic search?

Semantic search retrieves results based on meaning, not only exact word matching. It compares vector representations of the query and documents.

---

### Q5. What is a vector in this project?

A vector is a list of numbers generated from a code chunk or user query. It represents the meaning of that text in numerical form.

---

### Q6. Why do similar texts have similar vectors?

The embedding model is trained to place semantically related texts closer together in vector space.

---

### Q7. What is normalization?

Normalization makes all vectors have the same length while keeping their direction the same.

---

### Q8. Why is vector direction important?

In embedding search, vector direction represents semantic meaning. If two vectors point in similar directions, their meanings are likely similar.

---

### Q9. Why normalize embeddings?

I normalize embeddings so that similarity comparison focuses on direction rather than vector size. With normalized vectors, inner product search can behave like cosine similarity.

---

### Q10. What is cosine similarity?

Cosine similarity measures how close two vectors are in direction. It is commonly used to compare embeddings.

---

### Q11. What is dot product?

Dot product is a mathematical operation used to compare two vectors. For normalized vectors, dot product can be used like cosine similarity.

---

### Q12. Why use FAISS?

FAISS helps search through many vectors quickly. It is useful when we have thousands of code chunks and need to find the most relevant chunks for a user query.

---

### Q13. Is FAISS a vector database?

FAISS is better described as a vector similarity search library or vector index. It searches vectors efficiently, but we still need a separate metadata store for file paths, line numbers, and chunk content.

---

### Q14. What does FAISS return?

FAISS returns the IDs of the closest vectors and their similarity scores. We then use metadata mapping to find the original code chunk.

---

### Q15. Why do we need metadata with FAISS?

FAISS only knows about vectors and IDs. Metadata is needed to map each vector ID back to the original source file, line numbers, language, and chunk content.

---

### Q16. Why use the same model for chunks and queries?

Both chunk vectors and query vectors must exist in the same vector space. If different models are used, similarity comparison may not be meaningful.

---

### Q17. Why did you choose `all-MiniLM-L6-v2`?

I chose it as a lightweight and free baseline model. It is fast, easy to run locally, and good for building the first working retrieval pipeline.

---

### Q18. Is `all-MiniLM-L6-v2` the best model for code?

Not necessarily. It is a good starting baseline, but later I can compare it with code-specific embedding models using retrieval evaluation metrics.

---

### Q19. Why wrap SentenceTransformer in an `EmbeddingModel` class?

I wrapped it to create a clean abstraction. This makes it easier to replace the model, add caching, add batching, and test the code without depending directly on the external library everywhere.

---

### Q20. What is the role of embeddings in the full RAG pipeline?

Embeddings convert code chunks and questions into vectors. These vectors allow the retriever to find the most relevant chunks, which are then passed to the LLM for answer generation.

---

### Q21. Why not send the whole repository directly to the LLM?

Repositories can be very large, and LLM context windows are limited. Sending the whole repository would be slow, costly, and noisy. RAG retrieves only the most relevant chunks before generating an answer.

---

### Q22. What is the difference between embedding storage and metadata storage?

Embedding storage stores numerical vectors for similarity search. Metadata storage stores information about each vector, such as file path, line numbers, language, and chunk content.

---

### Q23. What is the complete retrieval flow after embeddings are created?

The user question is embedded into a query vector. FAISS compares it with stored chunk vectors and returns the closest vector IDs. The system then uses metadata to recover the original chunks and sends them to the LLM as context.

---

### Q24. What is one limitation of this embedding approach?

A general-purpose embedding model may not fully understand programming-language structure. Later improvements can include code-specific embedding models, hybrid search, reranking, and AST-based chunking.

---

### Q25. How would you improve this embedding layer later?

I would improve it by:

* testing code-specific embedding models
* adding batch processing
* caching embeddings
* evaluating retrieval quality
* combining semantic search with keyword search
* adding reranking
* preserving richer metadata
