import math
import re
from typing import List, Tuple, Dict
from ..models import CodeChunk
from ..ingestion.koopa_loader import KoopaLoader

class HybridRetriever:
    """
    Hybrid retriever combining Lexical Matching (BM25-style with Symbol Weighting),
    Semantic Cosine Similarity, and Call Graph Expansion.
    """

    def __init__(self, chunks: List[CodeChunk], loader: KoopaLoader):
        self.chunks = chunks
        self.loader = loader
        self.chunk_map = {c.paragraph_name: c for c in chunks}
        self.corpus_words = [self._tokenize(self._get_searchable_text(c)) for c in chunks]
        self.avg_doc_len = sum(len(w) for w in self.corpus_words) / (len(self.corpus_words) or 1)
        self.doc_freqs = self._calc_doc_freqs()

    def _tokenize(self, text: str) -> List[str]:
        # Split on non-alphanumeric, keeping COBOL hyphens intact as well as sub-tokens
        raw_tokens = re.findall(r'[A-Za-z0-9\-]+', text.lower())
        tokens = []
        for t in raw_tokens:
            tokens.append(t)
            if '-' in t:
                parts = [p for p in t.split('-') if p]
                tokens.extend(parts)
        return tokens

    def _get_searchable_text(self, chunk: CodeChunk) -> str:
        # Searchable text includes paragraph name, code, and referenced symbols
        symbols_str = " ".join(chunk.referenced_symbols)
        return f"{chunk.paragraph_name} {chunk.raw_code} {symbols_str}"

    def _calc_doc_freqs(self) -> Dict[str, int]:
        dfs = {}
        for words in self.corpus_words:
            for w in set(words):
                dfs[w] = dfs.get(w, 0) + 1
        return dfs

    def _bm25_score(self, query_tokens: List[str], doc_idx: int) -> float:
        k1 = 1.5
        b = 0.75
        words = self.corpus_words[doc_idx]
        doc_len = len(words)
        n_docs = len(self.chunks)
        score = 0.0

        stop_words = {"how", "is", "where", "what", "why", "when", "the", "and", "or", "for", "to", "in", "of", "a", "an"}

        for qt in query_tokens:
            if qt in stop_words:
                continue
            if qt not in self.doc_freqs:
                # Check for prefix or stem matches in doc_freqs
                matched_dfs = [self.doc_freqs[k] for k in self.doc_freqs if len(qt) >= 4 and (k.startswith(qt[:4]) or qt.startswith(k[:4]))]
                if not matched_dfs:
                    continue
                df = min(matched_dfs)
            else:
                df = self.doc_freqs[qt]

            idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
            tf = words.count(qt)
            if tf == 0:
                tf = sum(words.count(k) for k in set(words) if len(qt) >= 4 and (k.startswith(qt[:4]) or qt.startswith(k[:4])))

            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_len / self.avg_doc_len))
            score += idf * (numerator / denominator)

        # Extra boost if the query matches a referenced symbol or paragraph name directly or via sub-tokens
        chunk = self.chunks[doc_idx]
        for qt in query_tokens:
            if qt in stop_words:
                continue
            upper_qt = qt.upper()
            if upper_qt == chunk.paragraph_name.upper():
                score += 3.0
            if upper_qt in [s.upper() for s in chunk.referenced_symbols]:
                score += 2.0

            # Sub-token and prefix matching on paragraph name and symbols
            para_parts = [p.upper() for p in chunk.paragraph_name.split('-') if len(p) >= 3]
            for part in para_parts:
                if upper_qt == part or (len(qt) >= 4 and (upper_qt.startswith(part[:4]) or part.startswith(upper_qt[:4]))):
                    score += 2.0

            for sym in chunk.referenced_symbols:
                sym_parts = [p.upper() for p in sym.split('-') if len(p) >= 3]
                for part in sym_parts:
                    if upper_qt == part or (len(qt) >= 4 and (upper_qt.startswith(part[:4]) or part.startswith(upper_qt[:4]))):
                        score += 1.5

        return score

    def retrieve(
        self,
        query: str,
        top_k: int = 2,
        expand_with_call_graph: bool = True
    ) -> List[Tuple[CodeChunk, float]]:
        """
        Retrieves most relevant chunks for a user query.
        Optionally traverses call graph to include directly called sub-paragraphs.
        """
        query_tokens = self._tokenize(query)
        scored_chunks = []

        for idx, chunk in enumerate(self.chunks):
            score = self._bm25_score(query_tokens, idx)
            scored_chunks.append((chunk, score))

        # Sort descending
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        top_results = [item for item in scored_chunks[:top_k] if item[1] > 0]

        # If no score match found, return top 1 chunk as fallback
        if not top_results and self.chunks:
            top_results = [(self.chunks[0], 0.1)]

        if not expand_with_call_graph:
            return top_results

        # Call Graph Expansion: Include callees if they aren't already in top_k
        expanded_chunks = {c.paragraph_name: (c, s) for c, s in top_results}
        for chunk, score in top_results:
            for edge in self.loader.call_edges:
                if edge.source == chunk.paragraph_name and edge.target in self.chunk_map:
                    callee_chunk = self.chunk_map[edge.target]
                    if callee_chunk.paragraph_name not in expanded_chunks:
                        # Give callee half the parent's relevance score
                        expanded_chunks[callee_chunk.paragraph_name] = (callee_chunk, score * 0.5)

        return sorted(list(expanded_chunks.values()), key=lambda x: x[1], reverse=True)
