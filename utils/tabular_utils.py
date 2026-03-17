import pandas as pd

def build_tag_comparison_table(model1_tags, model2_tags, original_tags, extra_limit=5):
    # Convert to sets
    set1 = set(model1_tags)
    set2 = set(model2_tags)
    set_orig = set(original_tags)

    # Keep all original tags + up to extra_limit extra tags from models
    extra1 = [t for t in model1_tags if t not in set_orig][:extra_limit]
    extra2 = [t for t in model2_tags if t not in set_orig][:extra_limit]

    combined_tags = list(set_orig) + extra1 + extra2
    combined_tags = list(dict.fromkeys(combined_tags))  # remove duplicates

    # Compute match count per tag
    tag_match_count = {}
    for tag in combined_tags:
        count = sum([
            tag in set1,
            tag in set2,
            tag in set_orig
        ])
        tag_match_count[tag] = count

    # Sort tags by match count descending (all 3 → 2 → 1)
    sorted_tags = sorted(combined_tags, key=lambda x: (-tag_match_count[x], x))

    # Build DataFrame rows
    row1 = [tag if tag in set1 else "" for tag in sorted_tags]
    row2 = [tag if tag in set2 else "" for tag in sorted_tags]
    row3 = [tag if tag in set_orig else "" for tag in sorted_tags]

    df = pd.DataFrame(
        [row1, row2, row3],
        index=["Model 1", "Model 2", "Original Tags"],
        columns=sorted_tags
    )

    return df