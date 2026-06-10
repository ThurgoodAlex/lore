from lore.config import Config
from lore.ingestion.embedder import embed_text
from lore.storage.chroma import query_all


boost = {"adr": 1.15, "commit": 1.1, "doc": 1.05, "code": 1.0}

def retrieve(query: str, config: Config) -> list[dict]:
    """Given a query string, return a list of relevant documents."""
    count = {}  # track seen doc IDs to avoid duplicates across collections
    results = [] # final scored results to return
    # Embed the query
    query_embedding = embed_text(query, config)
    # Retrieve relevant documents from the vector store
    query_res = query_all(query_embedding, config.context.top_k)
    filtered_res = []
    for result in query_res:
        similarity = 1 - result['distance']
        if similarity > config.context.similarity_threshold:
            result['similarity'] = similarity
            filtered_res.append(result)
    for r in filtered_res:
        r['score'] = r['similarity'] * boost.get(r['metadata']['source_type'], 1.0)
    sorted_res = sorted(filtered_res, key=lambda x: x['score'], reverse=True)
    for r in sorted_res:
        file_id = r['metadata']['file_path']
        if file_id not in count:
            count[file_id] = 0
        else:
            count[file_id] += 1
        if count[file_id] >= 3:
            continue
        results.append(r)
    return results
