"""
Migration script: Local Qdrant -> Qdrant Cloud
Transfers all collections and their vectors from local storage to cloud.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv
import os
from tqdm import tqdm

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')

def migrate_qdrant_to_cloud():
    """Migrate all collections from local Qdrant to Qdrant Cloud."""

    print("="*60)
    print("QDRANT MIGRATION: LOCAL -> CLOUD")
    print("="*60)

    # Validate cloud credentials
    if not QDRANT_URL or not QDRANT_API_KEY:
        print("❌ Error: QDRANT_URL and QDRANT_API_KEY must be set in .env file")
        return False

    print(f"\n📍 Source: Local storage (./qdrant_storage)")
    print(f"📍 Destination: {QDRANT_URL}")

    # Initialize clients
    try:
        print("\n🔌 Connecting to local Qdrant...")
        local_client = QdrantClient(
            path="./qdrant_storage",
            force_disable_check_same_thread=True
        )

        print("🔌 Connecting to Qdrant Cloud...")
        cloud_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=60
        )

        print("✓ Both connections established\n")

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

    # Get all local collections
    try:
        local_collections = local_client.get_collections().collections
        print(f"📚 Found {len(local_collections)} local collections:")
        for col in local_collections:
            info = local_client.get_collection(col.name)
            print(f"  • {col.name}: {info.points_count} vectors")

        if not local_collections:
            print("⚠️  No collections found in local storage. Nothing to migrate.")
            return True

    except Exception as e:
        print(f"❌ Error listing local collections: {e}")
        return False

    # Migrate each collection
    for collection in local_collections:
        collection_name = collection.name
        print(f"\n{'='*60}")
        print(f"Migrating collection: {collection_name}")
        print(f"{'='*60}")

        try:
            # Get collection info
            local_info = local_client.get_collection(collection_name)
            vector_size = local_info.config.params.vectors.size
            distance = local_info.config.params.vectors.distance
            points_count = local_info.points_count

            print(f"Vector size: {vector_size}")
            print(f"Distance metric: {distance}")
            print(f"Total points: {points_count}")

            if points_count == 0:
                print("⚠️  Empty collection, skipping...")
                continue

            # Create collection in cloud (delete if exists)
            try:
                cloud_client.get_collection(collection_name)
                print(f"⚠️  Collection '{collection_name}' already exists in cloud. Deleting...")
                cloud_client.delete_collection(collection_name)
            except:
                pass

            print(f"Creating collection in cloud...")
            cloud_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance
                )
            )
            print("✓ Collection created in cloud")

            # Migrate points in batches
            batch_size = 100
            offset = None
            migrated_count = 0

            print(f"\n📤 Uploading vectors (batch size: {batch_size})...")

            with tqdm(total=points_count, desc="Migrating") as pbar:
                while True:
                    # Scroll through local points
                    records, next_offset = local_client.scroll(
                        collection_name=collection_name,
                        limit=batch_size,
                        offset=offset,
                        with_payload=True,
                        with_vectors=True
                    )

                    if not records:
                        break

                    # Convert Record objects to PointStruct
                    from qdrant_client.models import PointStruct
                    points = [
                        PointStruct(
                            id=record.id,
                            vector=record.vector,
                            payload=record.payload
                        )
                        for record in records
                    ]

                    # Upload to cloud
                    cloud_client.upsert(
                        collection_name=collection_name,
                        points=points
                    )

                    migrated_count += len(records)
                    pbar.update(len(records))

                    # Check if we've reached the end
                    if next_offset is None:
                        break

                    offset = next_offset

            # Verify migration
            cloud_info = cloud_client.get_collection(collection_name)
            cloud_count = cloud_info.points_count

            print(f"\n✓ Migration complete!")
            print(f"  Local vectors: {points_count}")
            print(f"  Cloud vectors: {cloud_count}")

            if cloud_count == points_count:
                print(f"  ✅ Success! All vectors migrated.")
            else:
                print(f"  ⚠️  Warning: Count mismatch!")

        except Exception as e:
            print(f"❌ Error migrating collection '{collection_name}': {e}")
            import traceback
            traceback.print_exc()
            continue

    # Final summary
    print(f"\n{'='*60}")
    print("MIGRATION SUMMARY")
    print(f"{'='*60}")

    cloud_collections = cloud_client.get_collections().collections
    print(f"\n📊 Cloud collections after migration:")
    total_vectors = 0
    for col in cloud_collections:
        info = cloud_client.get_collection(col.name)
        print(f"  • {col.name}: {info.points_count} vectors")
        total_vectors += info.points_count

    print(f"\n✅ Total vectors in cloud: {total_vectors}")
    print(f"✅ Migration complete!")

    return True


if __name__ == "__main__":
    success = migrate_qdrant_to_cloud()
    exit(0 if success else 1)
