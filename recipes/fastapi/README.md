# FastAPI Recipe

This is a simple FastAPI example with a `src` layout.

## Structure

```
recipes/fastapi/
├── README.md
├── pyproject.toml
└── src/
    ├── __init__.py
    └── __main__.py
```

## Installation

Ensure you have Python 3.10+ installed.

```bash
cd recipes/fastapi
pip install -e .
```

## Running the App

You can run the application as a module:

```bash
python -m src
```

Or using the installed script:

```bash
fastapi-recipe
```

## Usage

Open your browser at [http://127.0.0.1:8000](http://127.0.0.1:8000).

You will see the JSON response:

```json
{"Hello": "World"}
```

### Interactive API Docs

Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
