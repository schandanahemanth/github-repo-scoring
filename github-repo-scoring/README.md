# GitHub Repository Scoring Service

Backend service for searching public GitHub repositories and ranking them with a custom popularity score.

## Overview

This project implements a small FastAPI service for a coding challenge.

The service:
- queries GitHub's public repository search API
- allows filtering by `language` and `created_after`
- returns raw repository results
- returns scored repository results using a configurable popularity formula

The service only searches public repositories. A GitHub token is optional and is used only to improve API rate limits.

## Challenge Brief

Build a backend application that scores GitHub repositories using the public GitHub search API.

The user should be able to filter repositories by:
- programming language
- earliest creation date

The application should assign a popularity score to each repository based on:
- stars
- forks
- recency of updates

## Requirements

- Python 3.11+
- pip

## Tech Stack

- FastAPI
- Pydantic
- httpx
- pytest
- black
- ruff

## Project Structure

```text
github-repo-scoring-service/
├── app/                        # Application package
│   ├── __init__.py
│   ├── api/                    # FastAPI route handlers and dependency wiring
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── clients/                # External service clients such as GitHub API access
│   │   ├── __init__.py
│   │   └── github_client.py
│   ├── core/                   # Shared application infrastructure like config and logging
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── config.py
│   │   └── logger.py
│   ├── main.py                 # FastAPI application entrypoint
│   ├── models.py               # Internal domain models used across services and clients
│   ├── schemas.py              # Request and response schemas exposed by the API
│   └── services/               # Application services for orchestration and scoring logic
│       ├── __init__.py
│       ├── repository_service.py
│       └── scoring_service.py
├── tests/                      # API and service tests
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_config.py
│   ├── test_github_client.py
│   ├── test_repository_service.py
│   └── test_scoring.py
├── .env.example                # Example environment configuration
├── .gitignore                  # Local environment and Python ignore rules
├── pyproject.toml              # Project metadata, dependencies, and tool configuration
└── README.md                   # Project overview, setup, and API documentation
```

## Setup

Create and activate your virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Optional formatting command:

```bash
black app tests
```

Optional linting command:

```bash
ruff check app tests
```

Copy the example environment file if needed:

```bash
cp .env.example .env
```

## Environment Variables

The application reads configuration from `.env`.

```env
GITHUB_TOKEN=
GITHUB_API_VERSION=2026-03-10
GITHUB_CACHE_TTL_SECONDS=300
SCORE_WEIGHT_STARS=0.5
SCORE_WEIGHT_FORKS=0.3
SCORE_WEIGHT_RECENCY=0.2
SCORE_RECENCY_DECAY_DAYS=90
```

Notes:
- `GITHUB_TOKEN` is optional for public repository search
- a token is recommended to avoid low unauthenticated rate limits
- repeated GitHub search results are cached in memory for the configured TTL
- scoring weights and decay can be tuned without code changes

## Run The Service

```bash
uvicorn app.main:app --reload
```

Open the docs at:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### `GET /health`

Simple health check endpoint.

### `GET /repositories`

Returns raw GitHub repository results.

Supported query parameters:
- `language`
- `created_after`
- `sort_by`: optional, one of `stars`, `forks`, `updated`
- `order`: optional, one of `asc`, `desc`
- `page`
- `per_page`

Example:

```bash
curl "http://127.0.0.1:8000/repositories?language=Python&created_after=2024-01-01&sort_by=stars&order=desc&page=1&per_page=30"
```

### `GET /repositories/scored`

Returns repositories fetched from GitHub and ranked locally using the popularity score.

Supported query parameters:
- `language`
- `created_after`
- `page`
- `per_page`

Example:

```bash
curl "http://127.0.0.1:8000/repositories/scored?language=Python&created_after=2024-01-01&page=1&per_page=30"
```

## GitHub Search Behavior

The service uses the GitHub repository search endpoint:

```text
GET https://api.github.com/search/repositories
```

Filter mapping:
- `language=Python` becomes `language:Python`
- `created_after=2024-01-01` becomes `created:>=2024-01-01`
so the endpoint to search Github repository using both the parameters, would be:
```
https://api.github.com/search/repositories?q=language:Python+created:>=2024-01-01&per_page=10&page=1&sort=forks&order=asc
```



For `GET /repositories`:
- optional raw sorting is passed through to GitHub

For `GET /repositories/scored`:
- no upstream GitHub sort is applied
- repositories are fetched using filters only
- scoring and final ranking happen locally
- repeated identical GitHub searches are served from the in-memory cache until the TTL expires

## Scoring Algorithm

The agreed popularity formula is:

```python
score = (
    0.5 * math.log1p(stars) +
    0.3 * math.log1p(forks) +
    0.2 * math.exp(-days_since_update / 90)
)
```

Interpretation:
- stars are the strongest popularity signal
- forks represent developer engagement
- recent updates add a freshness bonus

Design notes:
- `log1p` prevents very large repositories from dominating too strongly
- exponential decay rewards active maintenance
- the default weights and decay window are configurable through environment variables

Scoring uses the current page of GitHub results only, not the full GitHub result set.


## Running Tests

```bash
pytest
```

If you are using the virtual environment directly:

```bash
python -m pytest
```


## Error Handling

The service translates common GitHub API failures into clean HTTP responses:
- `401` for invalid GitHub authentication
- `403` for GitHub rate limiting or forbidden access
- `502` when the GitHub API is unavailable or a transport error occurs
- `504` when the GitHub API request times out

## Limitations

- only public GitHub repositories are supported
- repository data is fetched on demand and is not persisted
- scored ranking is applied only to the current GitHub search page requested by the user; GitHub returns paginated results with up to 100 repositories per page, and this version does not aggregate scores across multiple pages
- the service does not implement its own authentication or rate limiting; it relies on GitHub's public API and may be affected by upstream rate limits, especially without a configured `GITHUB_TOKEN`
- no caching layer is included in this version

## Future Enhancements

- switch to an async HTTP client if the service needs higher concurrency or parallel upstream calls
- support multi-page aggregation before scoring to produce broader ranked results
- add service-level authentication and rate limiting
- persist repository snapshots for analytics or historical comparisons
- expose a normalized display score in addition to the raw ranking score
