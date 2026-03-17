from vectorstore.qdrant_client import qdrant_service


COLLECTION_NAME = "medical_articles"  # put your actual collection name here


def main():
    client = qdrant_service.client

    try:
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if COLLECTION_NAME not in collection_names:
            print(f"❌ Collection '{COLLECTION_NAME}' does not exist.")
            return

        print(f"✅ Collection '{COLLECTION_NAME}' exists.")

        info = client.get_collection(COLLECTION_NAME)
        print("\nCollection Info:")
        print(info)

        count = client.count(collection_name=COLLECTION_NAME).count
        print(f"\nTotal records in Qdrant: {count}")

        print("\n🔎 Fetching sample records...")
        points, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=5,
            with_payload=True,
            with_vectors=False
        )

        for i, point in enumerate(points, 1):
            print(f"\nRecord {i}:")
            print("ID:", point.id)
            print("Payload keys:", list(point.payload.keys()))

    finally:
        client.close()   # 👈 THIS FIXES THE ERROR

if __name__ == "__main__":
    main()