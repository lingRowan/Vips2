from flask import Flask, request, render_template
from whoosh.qparser import QueryParser
from whoosh.index import open_dir, create_in
from whoosh.fields import Schema, TEXT, ID
import os

app = Flask(__name__, template_folder="template")
INDEX_DIR = "index"

# Function to create the index if it doesn't exist
def get_or_create_index(index_dir=INDEX_DIR):
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    if not os.listdir(index_dir):  # Check if the directory is empty
        # Define the schema for the index
        schema = Schema(title=TEXT(stored=True), url=ID(stored=True), content=TEXT(stored=True))
        # Create the index if it doesn't exist
        ix = create_in(index_dir, schema)
        
        # Optionally, add some documents to the index (for testing purposes)
        writer = ix.writer()
        writer.add_document(title="Example Title 1", url="http://example.com/1", content="This is the first example content.")
        writer.add_document(title="Example Title 2", url="http://example.com/2", content="This is the second example content.")
        writer.commit()
    else:
        # Open the existing index
        ix = open_dir(index_dir)
    return ix

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search")
def search():
    query = request.args.get("q", "")
    page = int(request.args.get("page", 1))  # Default to page 1
    results_per_page = 10
    results = []
    no_results = False  # Flag to indicate if no results are found
    total_pages = 0

    if query:
        try:
            ix = get_or_create_index()  # Ensure the index exists
            with ix.searcher() as searcher:
                query_parser = QueryParser("content", ix.schema)
                parsed_query = query_parser.parse(query)

                search_results = searcher.search(parsed_query, limit=None)  # Fetch all matching results

                # Get the total number of results
                total_results = len(search_results)

                # If there are no results, set the flag to True
                if total_results == 0:
                    no_results = True
                else:
                    # Paginate results
                    start = (page - 1) * results_per_page
                    end = start + results_per_page
                    paginated_results = search_results[start:end]

                    for result in paginated_results:
                        results.append({
                            "title": result["title"],
                            "url": result["url"],
                            "content": result.highlights("content") or result["content"][:200] + "..."
                        })

                    # Calculate the total number of pages
                    total_pages = (total_results // results_per_page) + (1 if total_results % results_per_page else 0)

        except Exception as e:
            print(f"Error during search: {e}")

    return render_template(
        "results.html", 
        query=query, 
        results=results, 
        no_results=no_results, 
        page=page, 
        total_pages=total_pages
    )

if __name__ == "__main__":
    app.run(debug=True)
