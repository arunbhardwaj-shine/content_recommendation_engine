from typing import Optional
from chromadb.api.models.Collection import Collection


def inspect_collection(
    collection: Collection,
    name: str,
    sample_size: int = 3,
    verbose: bool = True
):
    """
    Inspect a Chroma collection:
    - total vectors
    - embedding dimension
    - sample docs & metadata
    """

    print("\n" + "=" * 60)
    print(f"📦 Collection Name : {name}")

    try:
        count = collection.count()
        print(f"🔢 Total Records   : {count}")
    except Exception as e:
        print(f"❌ Failed to count records: {e}")
        return

    if count == 0:
        print("⚠️ Collection is empty")
        return

    # Fetch a small sample
    try:
        sample = collection.get(
            limit=min(sample_size, count),
            include=["documents", "metadatas"]
        )

        print(f"🧪 Sample Records  : {len(sample['ids'])}")

        for i in range(len(sample["ids"])):
            print("\n--- Sample", i + 1, "---")
            print("ID        :", sample["ids"][i])
            print("Doc chars :", len(sample["documents"][i]))
            print("Metadata  :", sample["metadatas"][i])

            if verbose:
                print("Doc preview:")
                print(sample["documents"][i][:200], "...")

    except Exception as e:
        print(f"❌ Failed to fetch samples: {e}")

    print("=" * 60 + "\n")
