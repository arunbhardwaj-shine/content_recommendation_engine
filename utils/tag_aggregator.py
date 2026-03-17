import json
from collections import defaultdict
import math
import numpy as np

def aggregate_tags(results, alpha=0.7, eps=1e-6, min_confidence=0.55):
    """
    Combines similarity strength + chunk coverage.
    Returns non-repetitive tags with meaningful confidence.
    """

    metadatas = results["metadatas"]   # [chunks][top_k]
    distances = results["distances"]

    total_chunks = len(metadatas)

    # --- similarity scores ---
    tag_similarity_scores = defaultdict(list)

    # --- coverage ---
    tag_chunk_hits = defaultdict(set)

    for chunk_idx in range(total_chunks):
        for match_idx in range(len(metadatas[chunk_idx])):
            metadata = metadatas[chunk_idx][match_idx]
            distance = distances[chunk_idx][match_idx]

            raw_tags = metadata.get("tags")
            if not raw_tags:
                continue

            if isinstance(raw_tags, str):
                tags = json.loads(raw_tags)
            else:
                tags = raw_tags

            similarity_score = 1 - distance

            for tag in tags:
                tag_similarity_scores[tag].append(similarity_score)
                tag_chunk_hits[tag].add(chunk_idx)

    # --- normalize similarity ---
    tag_similarity = {
        tag: sum(scores) / len(scores)
    }

    max_sim = max(tag_similarity.values())

    # --- final aggregation ---
    aggregated = []
    for tag in tag_similarity:
        norm_sim = tag_similarity[tag] / max_sim
        coverage = len(tag_chunk_hits[tag]) / total_chunks

        final_conf = alpha * norm_sim + (1 - alpha) * coverage
        if final_conf >= min_confidence:
            aggregated.append({
                "tag": tag,
                "confidence": round(final_conf, 4)
            })

    aggregated.sort(key=lambda x: x["confidence"], reverse=True)
    return aggregated


def aggregate_tags_v1_sorted(
    results,
    alpha=0.7,
    min_confidence=0.55,
):
    metadatas = results["metadatas"]   # [chunks][top_k]
    distances = results["distances"]

    total_chunks = len(metadatas)
    if total_chunks == 0:
        return []

    tag_similarity_scores = defaultdict(list)
    tag_chunk_hits = defaultdict(set)

    for chunk_idx in range(total_chunks):
        for match_idx in range(len(metadatas[chunk_idx])):
            metadata = metadatas[chunk_idx][match_idx]
            distance = distances[chunk_idx][match_idx]

            raw_tags = metadata.get("tags")
            if not raw_tags:
                continue

            tags = json.loads(raw_tags) if isinstance(raw_tags, str) else raw_tags
            similarity = 1 - distance

            for tag in tags:
                tag_similarity_scores[tag].append(similarity)
                tag_chunk_hits[tag].add(chunk_idx)

    if not tag_similarity_scores:
        return []
    print(tag_similarity_scores,"SORTED")
    # --- average similarity per tag (same as v1) ---
    tag_similarity = {
        tag: sum(scores) / len(scores)
        for tag, scores in tag_similarity_scores.items()
    }

    max_sim = max(tag_similarity.values())

    # --- final confidence (same as v1) ---
    tag_scores = {}
    for tag in tag_similarity:
        norm_sim = tag_similarity[tag] / max_sim
        coverage = len(tag_chunk_hits[tag]) / total_chunks

        final_conf = alpha * norm_sim + (1 - alpha) * coverage
        if final_conf >= min_confidence:
            tag_scores[tag] = final_conf

    # --- sorted list of tag names only ---
    sorted_tags = [
        tag for tag, _ in
        sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)
    ]

    return sorted_tags


def aggregate_tagsv2(
    results,
    alpha=0.7,
    min_confidence=0.55,
    min_chunks=2,
    top_k_sim=3,
):
    metadatas = results.get("metadatas", [])
    distances = results.get("distances", [])

    total_chunks = len(metadatas)
    if total_chunks == 0:
        return []

    tag_similarity_scores = defaultdict(list)
    tag_chunk_hits = defaultdict(set)

    for chunk_idx in range(total_chunks):
        for match_idx, metadata in enumerate(metadatas[chunk_idx]):
            distance = distances[chunk_idx][match_idx]

            raw_tags = metadata.get("tags")
            if not raw_tags:
                continue

            tags = json.loads(raw_tags) if isinstance(raw_tags, str) else raw_tags

            # ✅ bounded similarity
            similarity = 1 - distance

            for tag in tags:
                tag_similarity_scores[tag].append(similarity)
                tag_chunk_hits[tag].add(chunk_idx)

    aggregated = []

    for tag, sims in tag_similarity_scores.items():
        # ❌ reject weakly supported tags
        if len(tag_chunk_hits[tag]) < min_chunks:
            continue

        # ✅ top-k similarity
        top_sims = sorted(sims, reverse=True)[:top_k_sim]
        sim_score = sum(top_sims) / len(top_sims)

        coverage = len(tag_chunk_hits[tag]) / total_chunks

        final_conf = alpha * sim_score + (1 - alpha) * coverage

        if final_conf >= min_confidence:
            aggregated.append({
                "tag": tag,
                "confidence": round(final_conf, 4),
                "coverage": round(coverage, 3)
            })

    aggregated.sort(key=lambda x: x["confidence"], reverse=True)
    return aggregated


def aggregate_tagsv2_sorted(results, alpha=0.7, min_chunks=2, min_confidence=0.55, top_k_sim=3):
    metadatas = results.get("metadatas", [])
    distances = results.get("distances", [])

    total_chunks = len(metadatas)
    if total_chunks == 0:
        return []

    tag_similarity_scores = defaultdict(list)
    tag_chunk_hits = defaultdict(set)

    for chunk_idx in range(total_chunks):
        for match_idx, metadata in enumerate(metadatas[chunk_idx]):
            distance = distances[chunk_idx][match_idx]

            raw_tags = metadata.get("tags")
            if not raw_tags:
                continue

            tags = json.loads(raw_tags) if isinstance(raw_tags, str) else raw_tags
            similarity = 1 - distance

            for tag in tags:
                tag_similarity_scores[tag].append(similarity)
                tag_chunk_hits[tag].add(chunk_idx)

    # Compute final relevance score
    tag_scores = {}
    for tag, sims in tag_similarity_scores.items():
        if len(tag_chunk_hits[tag]) < min_chunks:
            continue

        top_sims = sorted(sims, reverse=True)[:top_k_sim]
        sim_score = sum(top_sims) / len(top_sims)
        coverage = len(tag_chunk_hits[tag]) / total_chunks

        final_score = alpha * sim_score + (1 - alpha) * coverage
        if final_score >= min_confidence:
            tag_scores[tag] = final_score

    # Sort tags by score descending and return only tag names
    sorted_tags = [tag for tag, _ in sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)]
    return sorted_tags

def compute_domain_score(results):
    distances = [
        d
        for chunk in results["distances"]
        for d in chunk
    ]
    return sum(distances) / len(distances)


def compute_domain_scorev2(results, top_k=5, min_hits=3, sim_threshold=0.55):
    """
    Robust domain score. Returns 0 for out-of-domain PDFs.
    """
    distances = [
        d for chunk in results.get("distances", []) for d in chunk
    ]
    if not distances:
        return 0.0

    # Convert distance → similarity
    similarities = [1 - d for d in distances]

    # Take top_k similarities
    top_sim = sorted(similarities, reverse=True)[:top_k]

    # Reject if too few chunks hit threshold
    strong_hits = [s for s in top_sim if s >= sim_threshold]
    if len(strong_hits) < min_hits:
        return 0.0

    # Mean of top similarities
    return sum(top_sim) / len(top_sim)


def aggregate_tagsv3(results, alpha=0.7, eps=1e-6, min_confidence=0.55):

    metadatas = results.get("metadatas", [])
    distances = results.get("distances", [])

    if not metadatas or not distances:
        return []

    total_chunks = len(metadatas)

    tag_similarity_scores = defaultdict(list)
    tag_chunk_hits = defaultdict(set)

    for chunk_idx in range(total_chunks):
        for match_idx in range(len(metadatas[chunk_idx])):
            metadata = metadatas[chunk_idx][match_idx]
            distance = distances[chunk_idx][match_idx]

            raw_tags = metadata.get("tags")
            if not raw_tags:
                continue

            if isinstance(raw_tags, str):
                try:
                    tags = json.loads(raw_tags)
                except json.JSONDecodeError:
                    continue
            else:
                tags = raw_tags

            similarity_score = max(1 - distance, 0.0)

            for tag in tags:
                tag_similarity_scores[tag].append(similarity_score)
                tag_chunk_hits[tag].add(chunk_idx)

    # ---- FIXED PART ----
    if not tag_similarity_scores:
        return []

    tag_similarity = {
        tag: sum(score_list) / len(score_list)
        for tag, score_list in tag_similarity_scores.items()
    }

    max_sim = max(tag_similarity.values()) + eps

    aggregated = []
    for tag in tag_similarity:
        norm_sim = tag_similarity[tag] / max_sim
        coverage = len(tag_chunk_hits[tag]) / total_chunks

        final_conf = alpha * norm_sim + (1 - alpha) * coverage

        if final_conf >= min_confidence:
            aggregated.append({
                "tag": tag,
                "confidence": round(final_conf, 4)
            })

    aggregated.sort(key=lambda x: x["confidence"], reverse=True)
    return aggregated

def normalize_model_output(model_output):
    return {
        item["tag"]: float(item["confidence"])
        for item in model_output
    }


def build_ranked_aligned_results(original_tags, model1_tags, model2_tags):
    model1_map = normalize_model_output(model1_tags)
    model2_map = normalize_model_output(model2_tags)

    original_set = set(original_tags)
    model1_set = set(model1_map.keys())
    model2_set = set(model2_map.keys())

    all_tags = original_set | model1_set | model2_set

    def tag_score(tag):
        """
        Priority score:
        3 → present in all three
        2 → present in any two
        1 → present in only one
        """
        return int(tag in original_set) + int(tag in model1_set) + int(tag in model2_set)

    # Sort tags:
    # 1) by coverage (descending)
    # 2) by max confidence (descending) to stabilize ranking
    sorted_tags = sorted(
        all_tags,
        key=lambda t: (
            tag_score(t),
            max(
                model1_map.get(t, 0),
                model2_map.get(t, 0)
            )
        ),
        reverse=True
    )

    results = []

    for tag in sorted_tags:
        results.append({
            "original_tag": tag if tag in original_set else "",
            "model1_tag": tag if tag in model1_set else "",
            "model1_confidence": model1_map.get(tag, 0),
            "model2_tag": tag if tag in model2_set else "",
            "model2_confidence": model2_map.get(tag, 0)
        })

    return results

def build_ranked_aligned_resultsv2(original_tags, model1_tags, model2_tags):
    model1_map = normalize_model_output(model1_tags)
    model2_map = normalize_model_output(model2_tags)

    original_set = set(original_tags)
    model1_set = set(model1_map.keys())
    model2_set = set(model2_map.keys())

    all_tags = original_set | model1_set | model2_set

    def presence_count(tag):
        return (
            int(tag in original_set) +
            int(tag in model1_set) +
            int(tag in model2_set)
        )

    priority_1, priority_2 = [], []
    leftovers_model1, leftovers_model2, leftovers_original = [], [], []

    for tag in all_tags:
        count = presence_count(tag)
        if count == 3:
            priority_1.append(tag)
        elif count == 2:
            priority_2.append(tag)
        else:
            if tag in model1_set:
                leftovers_model1.append(tag)
            elif tag in model2_set:
                leftovers_model2.append(tag)
            else:
                leftovers_original.append(tag)

    def confidence_sort(tag):
        return max(model1_map.get(tag, 0), model2_map.get(tag, 0))

    priority_1 = sorted(priority_1, key=confidence_sort, reverse=True)
    priority_2 = sorted(priority_2, key=confidence_sort, reverse=True)

    results = []

    # Priority 1 & 2 (normal rows)
    for tag in priority_1 + priority_2:
        results.append({
            "original_tag": tag if tag in original_set else "",
            "model1_tag": tag if tag in model1_set else "",
            "model1_confidence": model1_map.get(tag, 0),
            "model2_tag": tag if tag in model2_set else "",
            "model2_confidence": model2_map.get(tag, 0)
        })

    # ---- MERGED leftovers ----
    max_len = max(
        len(leftovers_model1),
        len(leftovers_model2),
        len(leftovers_original)
    )

    for i in range(max_len):
        tag1 = leftovers_model1[i] if i < len(leftovers_model1) else ""
        tag2 = leftovers_model2[i] if i < len(leftovers_model2) else ""
        tag0 = leftovers_original[i] if i < len(leftovers_original) else ""

        results.append({
            "original_tag": tag0,
            "model1_tag": tag1,
            "model1_confidence": model1_map.get(tag1, 0) if tag1 else 0,
            "model2_tag": tag2,
            "model2_confidence": model2_map.get(tag2, 0) if tag2 else 0
        })

    return results

def build_ranked_aligned_results_pdf(model1_tags, model2_tags):
    model1_map = normalize_model_output(model1_tags)
    model2_map = normalize_model_output(model2_tags)

    model1_set = set(model1_map.keys())
    model2_set = set(model2_map.keys())

    # 1️⃣ Common tags
    common_tags = model1_set & model2_set

    def confidence(tag):
        return max(
            model1_map.get(tag, 0),
            model2_map.get(tag, 0)
        )

    common_sorted = sorted(common_tags, key=confidence, reverse=True)

    results = []

    # Common rows
    for tag in common_sorted:
        results.append({
            "original_tag": "",
            "model1_tag": tag,
            "model1_confidence": model1_map.get(tag, 0),
            "model2_tag": tag,
            "model2_confidence": model2_map.get(tag, 0)
        })

    # 2️⃣ Single tags (PAIR THEM)
    model1_only = sorted(
        model1_set - model2_set,
        key=lambda t: model1_map.get(t, 0),
        reverse=True
    )

    model2_only = sorted(
        model2_set - model1_set,
        key=lambda t: model2_map.get(t, 0),
        reverse=True
    )

    max_len = max(len(model1_only), len(model2_only))

    for i in range(max_len):
        tag1 = model1_only[i] if i < len(model1_only) else ""
        tag2 = model2_only[i] if i < len(model2_only) else ""

        results.append({
            "model1_tag": tag1,
            "model1_confidence": model1_map.get(tag1, 0) if tag1 else 0,
            "model2_tag": tag2,
            "model2_confidence": model2_map.get(tag2, 0) if tag2 else 0
        })

    return results