# Notes Assistant

A semantic search system for personal notes using FAISS and sentence transformers.

## Project Structure

After refactoring, the project has been organized into a cleaner structure:

### Core Module (`notes_core/`)
- `notes_core/__init__.py` - Contains all core functionality:
  - `NotesCore` class - Main class for notes management, indexing, and querying
  - `Note` model - Database model for notes

### CLI Wrapper (`notes_manager.py`)
- Simple command-line interface that directly initializes and uses `NotesCore`
- Handles argument parsing and high-level script entry
- No core logic - just CLI orchestration

### Other Files
- `config.py` - Configuration settings
- `api.py` - FastAPI web interface (unchanged)
- `notes.json` - Sample notes data
- `requirements.txt` - Python dependencies

## Usage

### Using the main CLI wrapper:
```bash
# Load notes from JSON to database
python notes_manager.py --load

# Build semantic search index
python notes_manager.py --build-index

# Query notes (interactive mode)
python notes_manager.py

# Query notes with specific query
python notes_manager.py --query "when is my flight"

# Query with custom number of results
python notes_manager.py --query "meeting" --k 3
```

### Using the core module programmatically:
```python
from notes_core import NotesCore

# Initialize core functionality
core = NotesCore()

# Load notes
core.load_notes_to_db()

# Build index
core.build_index()

# Search notes
results = core.search_notes("your query", k=5)

# Format results
formatted = core.format_results("your query", results)
```

## Benefits of Refactoring

1. **Single Source of Truth**: All core logic is now in `notes_core/__init__.py`
2. **No Duplication**: Logic is not duplicated between CLI and individual scripts
3. **Clean Separation**: CLI wrapper only handles argument parsing and orchestration
4. **Direct Usage**: CLI directly uses the NotesCore object without wrapper functions
5. **Programmatic Access**: Easy to use the core functionality in other Python code
6. **Maintainability**: Changes only need to be made in one place

## Dependencies

Install required packages:
```bash
pip install -r requirements.txt
``` 