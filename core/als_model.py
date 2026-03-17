import numpy as np
from implicit.als import AlternatingLeastSquares
import scipy.sparse as sparse


class ALSRecommender:

    def __init__(self):
        self.model = None

        # mappings
        self.user_mapping = {}
        self.user_reverse_mapping = {}

        self.item_mapping = {}
        self.reverse_item_mapping = {}

        self.sparse_matrix = None
        self.user_item_matrix = None

    def train(self, interaction_df):

        # ---------- Create categorical ids ----------
        interaction_df["user_id"] = interaction_df["user_id"].astype("category")
        interaction_df["pdf_id"] = interaction_df["pdf_id"].astype("category")

        # ---------- User mappings ----------
        self.user_mapping = dict(
            enumerate(interaction_df["user_id"].cat.categories)
        )

        self.user_reverse_mapping = {
            v: k for k, v in self.user_mapping.items()
        }

        # ---------- Item mappings ----------
        self.item_mapping = dict(
            enumerate(interaction_df["pdf_id"].cat.categories)
        )

        self.reverse_item_mapping = {
            v: k for k, v in self.item_mapping.items()
        }

        # ---------- Internal codes ----------
        user_codes = interaction_df["user_id"].cat.codes
        item_codes = interaction_df["pdf_id"].cat.codes

        # ---------- Sparse Matrix ----------
        self.sparse_matrix = sparse.coo_matrix(
            (interaction_df["strength"], (item_codes, user_codes))
        ).tocsr()

        # Precompute user-item matrix
        self.user_item_matrix = self.sparse_matrix.T.tocsr()

        # ---------- Train ALS ----------
        self.model = AlternatingLeastSquares(
            factors=40,
            regularization=0.1,
            iterations=20,
            use_gpu=False
        )

        self.model.fit(self.sparse_matrix)

    def recommend(self, real_user_id, top_n=3):

        if real_user_id not in self.user_reverse_mapping:
            return []

        user_internal_id = self.user_reverse_mapping[real_user_id]

        # Safety check (fix for your error)
        if user_internal_id >= self.user_item_matrix.shape[0]:
            return []

        user_row = self.user_item_matrix[user_internal_id]

        # Generate extra candidates
        item_ids, scores = self.model.recommend(
            user_internal_id,
            user_row,
            N=top_n * 5,
            filter_already_liked_items=True
        )

        results = []

        for item_internal_id, score in zip(item_ids, scores):

            if item_internal_id not in self.item_mapping:
                continue

            real_pdf_id = self.item_mapping[item_internal_id]

            results.append({
                "pdf_id": real_pdf_id,
                "score": round(float(score), 4)
            })

            if len(results) >= top_n:
                break

        return results