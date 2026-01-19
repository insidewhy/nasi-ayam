# nasi-ayam

`nasi-ayam` is a project to index `pdf`, `markdown` and `text` documents available locally and within a github directory. It provides a chatbot using Anthropic's `claude` LLM that utilises `RAG` to gather information based on these documents.

This tool was written to explore the viability of running RAG and data ingestion on the hardware available in conventional mid-range consumer grade laptops.

The project runs within docker images ensuring that local database setup is not necessary.

## Demonstration

![Demo](./docs/example.webp)

Note the initial load time is quite significant, LangChain dependencies are very large and take a while to import via python. Also note the first request takes a very long time to process, LangChain lazy loads various parts of its code the first time those paths are triggered which leads to high CPU usage and some delay. This and python's GIL explain why the loading spinners update so infrequently during these processes.

## Prerequisites

- Docker and Docker Compose
- [make](https://www.gnu.org/software/make/)
- An Anthropic API key
- nvidia-container-toolkit (optional, for GPU acceleration on Linux)

## Quick Start

```bash
export ANTHROPIC_API_KEY=your-key-here
./nasi-ayam
```

## Setup

Since this application runs within `docker` it will not be able to access local nvidia cards unless `nvidia-container-toolkit` has been installed and configured on Linux, or equivalent setup has been done on Windows/WSL2. `docker` implementations available for MacOS do not currently allow for this possibility.

## Configuration

The current configuration variables are supported:

- `ANTHROPIC_API_KEY`: An API key for `claude`, this must be available or the process will exit
- `RELEVANT_DOCUMENT_RESULT_COUNT`: The number of relevant documents to return after reranking, defaults to `5`
- `INITIAL_RETRIEVAL_COUNT`: The number of documents to retrieve from vector search before reranking, defaults to `10`
- `CHUNK_SIZE`: Vector chunk size in characters, defaults to `2000`
- `OVERLAP_SIZE`: Overlap between chunks in characters, defaults to `200`
- `SEMANTIC_CHUNK_SIZE`: Maximum semantic chunk size in characters, defaults to `8000`. Each vector chunk references one or more semantic chunks (e.g. the content of a section in a document) when there is an available semantic chunk within this size limit.
- `MAX_CONTEXT_CHARACTERS`: Conversation history character limit before compaction is triggered, defaults to `32000`
- `RERANKER_MODEL`: The cross-encoder model used for reranking search results, defaults to `cross-encoder/ms-marco-MiniLM-L-6-v2`
- `GITHUB_DATA_PATH`: The path to a remote github directory containing content to ingest, defaults to `https://github.com/insidewhy/nasi-ayam/tree/main/example-data/github`
- `LOCAL_DATA_PATH`: The path to a directory on the current machine to ingest, defaults to `example-data/local`
- `LOG_LEVEL`: The minimum level of logs to create, defaults to `INFO`. Logs will be stored in the `logs` directory within the project directory.

## Running the application

```bash
./nasi-ayam
```

The application will check remote/local sources for new data if they have not been ingested within the last 24 hours. The application will notify the user when all data has been ingested, after ingestion has completed it is possible to have conversations with the chatbot by typing a question into the terminal and pressing the enter key. The chatbot remembers conversation history across multiple invocations and compacts history as necessary.

[This document](./example-data/suggested-prompts.md) suggests some sample prompts that can be used to test the system with the example documents provided in this repository.

The application can also be invoked with a single prompt which will be issued after ingestion completes. In this instance the application will terminate after giving its response.

```bash
./nasi-ayam 'What animals communicate through body language rather than sounds'
```

The application can be run to perform migrations/ingestions only without prompting the user with the `-i` argument:

```bash
./nasi-ayam -i
```

The chat message history can be cleared with the `-c` argument:

```bash
./nasi-ayam -c
```

## Development

For local development (running tests, linting, etc.), set up a local Python environment:

```bash
make init-dev        # Install Python via pyenv and dependencies via poetry
```

This creates a `.venv` directory for local tooling. The Docker container uses its own Python environment.

### Makefile Targets

```bash
make init-dev        # Set up local dev environment (pyenv + poetry)
make reset-postgres  # Shut down postgres and remove its volume
make psql            # Open a psql session for debugging
make format          # Format code with black
make lint            # Lint code with flake8
make typecheck       # Checks typing with mypy
make test            # Run unit tests
make validate        # Runs format, lint, typecheck and test
```

## Troubleshooting

### Missing API key

If you see an error about a missing API key, ensure `ANTHROPIC_API_KEY` is exported in your environment before running the application.

### GPU not detected

Ensure `nvidia-container-toolkit` is installed and configured. You can verify with:

```bash
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### Database issues

If you encounter database problems or want to force data to be reingested, reset the postgres volume:

```bash
make reset-postgres
```

## Further reading

- [Detailed Specification](./specifications/nasi-ayam.md)
- [Suggested prompts against the bundled sample data](./example-data/suggested-prompts.md)
- [Overview presentation](./docs/overview.md)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
