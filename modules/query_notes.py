from notes_core import NotesQuery

def main():
    # Initialize query system
    query_system = NotesQuery()
    
    # Get user query
    query = input("Enter your question: ")
    
    # Search for relevant notes
    results = query_system.search_notes(query)
    
    if not results:
        print("No relevant notes found.")
        return
    
    # Format results
    formatted_results = query_system.format_results(query, results)
    print("\nSearch Results:")
    print(formatted_results)
    
    # Here you would typically send formatted_results to an LLM
    # for further processing/answering

if __name__ == "__main__":
    main() 