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

