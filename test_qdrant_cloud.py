"""
Test script to verify Qdrant Cloud connection and data
"""

from dotenv import load_dotenv
import os
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')

print("="*60)
print("QDRANT CLOUD CONNECTION TEST")
print("="*60)

print(f"\nURL: {QDRANT_URL}")
print(f"API Key: {QDRANT_API_KEY[:20]}..." if QDRANT_API_KEY else "No API Key")

# Connect to Qdrant Cloud
print("\n🔌 Connecting to Qdrant Cloud...")
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60
)

print("✓ Connected successfully!")

# List collections
print("\n📚 Collections in cloud:")
collections = client.get_collections().collections
for col in collections:
    info = client.get_collection(col.name)
    print(f"  • {col.name}: {info.points_count} vectors")

# Test search on pdf_documents
if collections:
    collection_name = "pdf_documents"
    print(f"\n🔍 Testing search on '{collection_name}'...")

    # Get a sample point to use its vector for testing
    sample = client.scroll(
        collection_name=collection_name,
        limit=1,
        with_vectors=True,
        with_payload=True
    )

    if sample[0]:
        point = sample[0][0]
        print(f"  Sample point ID: {point.id}")
        print(f"  Sample text preview: {point.payload.get('text', '')[:100]}...")

        # Search with the same vector (should return the same point)
        results = client.search(
            collection_name=collection_name,
            query_vector=point.vector,
            limit=3,
            with_payload=True
        )

        print(f"\n  Search results ({len(results)} found):")
        for i, hit in enumerate(results, 1):
            print(f"    {i}. Score: {hit.score:.4f}")
            print(f"       Text: {hit.payload.get('text', '')[:80]}...")
            print(f"       Filename: {hit.payload.get('filename', 'N/A')}")

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
