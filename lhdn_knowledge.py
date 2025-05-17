import json
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os

# Load the model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Small, fast and good quality model

# Sample LHDN rules
data = [
    {
        "category": "Lifestyle",
        "keywords": ["electronics", "books", "sports", "gadgets"],
        "limit": 2500,
        "description": "You can claim up to RM2,500 for purchases on lifestyle-related items such as electronics, sports equipment, and books."
    },
    {
        "category": "Medical",
        "keywords": ["clinic", "pharmacy", "medicine", "hospital"],
        "limit": 6000,
        "description": "You can claim up to RM6,000 for medical expenses including consultations, treatments, and medication."
    },
    {
        "category": "Parenting",
        "keywords": ["tuition", "school", "books", "education"],
        "limit": 2000,
        "description": "Parents can claim up to RM2,000 for education expenses related to their children."
    },
    {
        "category": "Insurance & EPF",
        "keywords": ["insurance", "epf", "kwsp"],
        "limit": 7000,
        "description": "You may claim up to RM7,000 for life insurance premiums and EPF contributions."
    },
    {
        "category": "Donations",
        "keywords": ["donation", "ngo", "zakat"],
        "limit": 99999,
        "description": "Donations to approved institutions are deductible subject to the allowable income percentage."
    }
]

texts = [d["description"] for d in data]

# Generate embeddings
print("Generating embeddings...")
vecs = model.encode(texts)
vecs = np.array(vecs).astype('float32')  # Convert to float32 for FAISS

# Store in FAISS
print("Creating FAISS index...")
index = faiss.IndexFlatL2(vecs.shape[1])
index.add(vecs)

# Save index and metadata
print("Saving files...")
faiss.write_index(index, "lhdn_index.faiss")
with open("lhdn_metadata.json", "w") as f:
    json.dump(data, f, indent=2)

print("Knowledge base created successfully!")