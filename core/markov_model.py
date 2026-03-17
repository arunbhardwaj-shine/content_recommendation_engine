from collections import defaultdict

class MarkovRecommender:

    def __init__(self):
        self.transition_probs = {}

    def train(self, df):
        transition_counts = defaultdict(lambda: defaultdict(int))

        for user_id, group in df.groupby("user_id"):
            sequence = group["pdf_id"].tolist()

            for i in range(len(sequence) - 1):
                current_pdf = sequence[i]
                next_pdf = sequence[i + 1]
                transition_counts[current_pdf][next_pdf] += 1

        # Convert to probabilities
        for current_pdf, next_dict in transition_counts.items():
            total = sum(next_dict.values())

            self.transition_probs[current_pdf] = {
                next_pdf: count / total
                for next_pdf, count in next_dict.items()
            }

    def recommend(self, pdf_id, top_n=3):

        transitions = self.transition_probs.get(pdf_id)
        if not transitions:
            return []

        # Remove self-transition first (cleaner)
        filtered = {
            pdf: score
            for pdf, score in transitions.items()
            if pdf != pdf_id
        }

        if not filtered:
            return []

        # Sort and slice
        sorted_items = sorted(
            filtered.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        return [
            {
                "pdf_id": pdf,
                "score": round(score, 4)
            }
            for pdf, score in sorted_items
        ]