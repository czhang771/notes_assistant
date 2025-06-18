import argparse
import sys

from notes_core import NotesCore

def main():
    parser = argparse.ArgumentParser(description='Notes Manager - Semantic Search for Notes')
    parser.add_argument('--load', action='store_true', help='Load notes from JSON to database')
    parser.add_argument('--build-index', action='store_true', help='Build semantic search index')
    parser.add_argument('--query', type=str, help='Query notes (interactive if not provided)')
    parser.add_argument('--k', type=int, default=5, help='Number of results to return (default: 5)')
    
    args = parser.parse_args()

    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return

    # Initialize the core functionality
    try:
        core = NotesCore()
    except Exception as e:
        print(f"Error initializing NotesCore: {e}")
        sys.exit(1)

    # Load notes to database
    if args.load:
        print("Loading notes to database...")
        core.load_notes_to_db()
        print("Done loading notes.")

    # Build index
    if args.build_index:
        print("Building semantic search index...")
        core.build_index()
        print("Done building index.")

    # Query notes - only if query is explicitly provided or if no other actions were taken
    if args.query is not None or (not args.load and not args.build_index):
        try:
            # If query provided as argument, use it
            if args.query:
                query = args.query
            else:
                # Interactive mode
                print("\nEnter your question (or 'quit' to exit):")
                while True:
                    query = input("> ")
                    if query.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    results = core.search_notes(query, k=args.k)
                    
                    if not results:
                        print("No relevant notes found.")
                        continue
                    
                    formatted_results = core.format_results(query, results)
                    print("\nSearch Results:")
                    print(formatted_results)
                    print("\nEnter another question (or 'quit' to exit):")
                return

            # Process single query
            results = core.search_notes(query, k=args.k)
            
            if not results:
                print("No relevant notes found.")
                return
            
            formatted_results = core.format_results(query, results)
            print("\nSearch Results:")
            print(formatted_results)

        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Please run '--load' and '--build-index' first.")
            sys.exit(1)

if __name__ == "__main__":
    main() 