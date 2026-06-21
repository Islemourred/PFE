"""
SapBERT Normalizer — Semantic similarity matching using SapBERT.
When the Rule Engine fails to find an exact match, SapBERT encodes the
entity text and finds the closest HPO concept via cosine similarity.
This is the "AI" half of the hybrid approach (State of the Art §2.6).

Includes disk caching: the HPO vector index is computed once and saved
to a .npz file. Subsequent loads take < 1 second.
"""

import os
import time
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from log_config import get_logger

logger = get_logger(__name__)


class SapBERTLinker:
    """
    Uses SapBERT (cambridgeltl/SapBERT-from-PubMedBERT-fulltext) to encode
    medical phrases into vectors, then finds the closest HPO concept via
    cosine similarity.
    """

    # Adaptive threshold parameters
    MARGIN_HIGH = 0.18       # If margin > this, model is very confident
    MARGIN_LOW = 0.05        # If margin < this, model is unsure
    ADAPTIVE_MIN = 0.62      # Absolute floor — never accept below this
    CONTEXT_BOOST = False    # Disabled: SapBERT is trained on isolated terms

    def __init__(
        self,
        hpo_terms: list[dict],
        model_name: str = "cambridgeltl/SapBERT-from-PubMedBERT-fulltext",
        similarity_threshold: float = 0.68,
        batch_size: int = 128,
        cache_path: str = None,
    ):
        """
        Args:
            hpo_terms:            list of HPO term dicts from hpo_parser
            model_name:           HuggingFace model ID for SapBERT
            similarity_threshold: base cosine similarity threshold
            batch_size:           batch size for encoding HPO terms
            cache_path:           path to save/load the precomputed index (.npz)
        """
        self.threshold = similarity_threshold
        self.batch_size = batch_size

        logger.info("Loading SapBERT model: %s", model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

        # Try to load cached index, otherwise build and save it
        if cache_path is None:
            cache_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "sapbert_hpo_index.npz"
            )
        self.cache_path = cache_path

        if os.path.exists(cache_path):
            self._load_index(cache_path)
        else:
            self._build_index(hpo_terms)
            self._save_index(cache_path)

    def _encode(self, texts: list[str]) -> np.ndarray:
        """
        Encode a list of texts into normalized vectors using SapBERT.

        Args:
            texts: list of medical phrases

        Returns:
            numpy array of shape (N, 768) with L2-normalized vectors
        """
        all_vecs = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            tokens = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=64,
                return_tensors="pt",
            )
            with torch.no_grad():
                output = self.model(**tokens)
            # Use [CLS] token embedding
            vecs = output.last_hidden_state[:, 0, :].numpy()
            all_vecs.append(vecs)

            # Progress indicator
            done = min(i + self.batch_size, len(texts))
            logger.debug("  Encoding: %d/%d texts...", done, len(texts))

        # Progress complete
        all_vecs = np.vstack(all_vecs)
        # L2 normalize for cosine similarity via dot product
        norms = np.linalg.norm(all_vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1  # avoid division by zero
        return all_vecs / norms

    def _build_index(self, hpo_terms: list[dict]):
        """
        Pre-compute SapBERT vectors for all HPO terms.
        For each HPO term, we encode the label + all synonyms and keep
        the average representation.
        """
        logger.info("Building SapBERT HPO index (first time only, will be cached)...")
        start = time.time()

        # Collect all texts to encode: each HPO term's label + synonyms
        self.hpo_ids = []
        self.hpo_names = []
        texts_to_encode = []
        text_to_hpo_idx = []

        for i, term in enumerate(hpo_terms):
            name = term["name"]
            if not name:
                continue

            self.hpo_ids.append(term["id"])
            self.hpo_names.append(name)
            idx = len(self.hpo_ids) - 1

            # Encode the official label
            texts_to_encode.append(name)
            text_to_hpo_idx.append(idx)

            # Also encode synonyms (they share the same HPO ID)
            for syn in term.get("exact_synonyms", []):
                texts_to_encode.append(syn)
                text_to_hpo_idx.append(idx)

        logger.info("  Total texts to encode: %d (%d unique HPO terms)",
                    len(texts_to_encode), len(self.hpo_ids))

        all_vectors = self._encode(texts_to_encode)

        # For each HPO term, compute the average of all its vectors
        n_terms = len(self.hpo_ids)
        self.index = np.zeros((n_terms, all_vectors.shape[1]), dtype=np.float32)
        counts = np.zeros(n_terms, dtype=np.int32)

        for vec_idx, hpo_idx in enumerate(text_to_hpo_idx):
            self.index[hpo_idx] += all_vectors[vec_idx]
            counts[hpo_idx] += 1

        # Average and re-normalize
        for i in range(n_terms):
            if counts[i] > 0:
                self.index[i] /= counts[i]
        norms = np.linalg.norm(self.index, axis=1, keepdims=True)
        norms[norms == 0] = 1
        self.index = self.index / norms

        elapsed = round(time.time() - start, 1)
        logger.info("  SapBERT index built: %d terms in %ss", n_terms, elapsed)

    def _save_index(self, path: str):
        """Save precomputed index to disk for instant future loading."""
        np.savez_compressed(
            path,
            index=self.index,
            hpo_ids=np.array(self.hpo_ids),
            hpo_names=np.array(self.hpo_names),
        )
        size_mb = os.path.getsize(path) / (1024 * 1024)
        logger.info("  Index cached to %s (%.1f MB)", path, size_mb)

    def _load_index(self, path: str):
        """Load precomputed index from disk (< 1 second)."""
        logger.info("  Loading cached SapBERT index from %s...", path)
        start = time.time()
        data = np.load(path, allow_pickle=True)
        self.index = data["index"]
        self.hpo_ids = data["hpo_ids"].tolist()
        self.hpo_names = data["hpo_names"].tolist()
        elapsed = round(time.time() - start, 2)
        logger.info("  Loaded %d term vectors in %ss", len(self.hpo_ids), elapsed)

    def link(self, text: str, top_k: int = 3, context: str = None) -> dict | None:
        """
        Find the closest HPO concept using cosine similarity with
        adaptive margin-based threshold and optional contextual encoding.

        Args:
            text:    entity text (already abbreviation-expanded)
            top_k:   number of top candidates to consider
            context: optional surrounding sentence for disambiguation

        Returns:
            Best match dict or None if below adaptive threshold
        """
        # Contextual encoding: for short/ambiguous entities, prepend context
        if context and self.CONTEXT_BOOST and len(text.split()) <= 2:
            query_text = f"{text} [SEP] {context[:200]}"
        else:
            query_text = text

        # Encode the query
        query_vec = self._encode([query_text])  # shape (1, 768)

        # Cosine similarity = dot product (both are L2-normalized)
        similarities = np.dot(self.index, query_vec.T).flatten()

        # Get top-k indices
        top_indices = similarities.argsort()[-top_k:][::-1]

        # Build alternatives list
        alternatives = []
        for idx in top_indices:
            alternatives.append({
                "id": self.hpo_ids[idx],
                "name": self.hpo_names[idx],
                "score": round(float(similarities[idx]), 4),
            })

        best_idx = top_indices[0]
        best_score = float(similarities[best_idx])

        # ── Adaptive margin-based threshold ──
        # Instead of a fixed cutoff, use the margin between top-1 and top-2
        second_score = float(similarities[top_indices[1]]) if len(top_indices) > 1 else 0.0
        margin = best_score - second_score

        accepted = False
        if best_score >= self.threshold:
            # Standard acceptance — above base threshold
            accepted = True
        elif margin > self.MARGIN_HIGH and best_score >= self.ADAPTIVE_MIN:
            # High confidence margin — model clearly distinguishes this entity
            # Accept even though absolute score is below base threshold
            accepted = True
        elif margin < self.MARGIN_LOW and best_score < self.threshold + 0.05:
            # Low margin — top-1 and top-2 are too close, reject even if near threshold
            accepted = False

        if not accepted:
            return None

        return {
            "id": self.hpo_ids[best_idx],
            "name": self.hpo_names[best_idx],
            "match_type": "sapbert_similarity",
            "confidence": round(best_score, 4),
            "margin": round(margin, 4),
            "alternatives": alternatives,
        }
