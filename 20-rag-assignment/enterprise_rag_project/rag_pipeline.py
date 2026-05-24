from retrieval import search

def ask(query):

    results = search(query)

    context = "\n\n".join(results)

    response = f"""
Relevant Policy Information:

{context}
"""

    return response