"""Corpus-level signals: whole corpus in, one (non_obf, obf) affinity matrix out.

Distinct from ``scoring/``, which compares exactly two entities and knows nothing of the
corpus, and from ``matching/``, which selects and commits pairs. Nothing here may import
``matching/``.
"""
