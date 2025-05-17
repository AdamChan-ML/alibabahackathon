import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load the model - use the same model as in knowledge creation
model = SentenceTransformer('all-MiniLM-L6-v2')

with open("lhdn_metadata.json") as f:
    metadata = json.load(f)

index = faiss.read_index("lhdn_index.faiss")

def retrieve_relevant_rules(query, k=3):
    # Generate embedding for the query
    vec = model.encode([query])
    vec = np.array(vec).astype('float32')
    
    # Search for similar rules
    D, I = index.search(vec, k)
    return [metadata[i] for i in I[0]]