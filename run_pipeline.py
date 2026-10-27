#!/usr/bin/env python3
"""
End-to-End Pipeline for COBOL Knowledge Extraction with Code RAG.
Demonstrates:
1. Ingestion of Koopa Parser Artifacts (AST, Symbol Table, Call Graph)
2. AST-Aware Paragraph Chunking
3. Hybrid Lexical & Graph Retrieval
4. Symbol Table Pruning & Context Assembly
5. Business Rule Extraction
6. Quantitative Ablation Evaluation
"""

import os
import sys
import json

# Ensure local modules are accessible
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from src.ingestion.koopa_loader import KoopaLoader
from src.chunking.ast_chunker import ASTChunker
from src.slicing.context_slicer import ContextSlicer
from src.retrieval.hybrid_retriever import HybridRetriever
from src.extraction.rule_extractor import RuleExtractor
from evaluation.benchmark import Evaluator

def main():
    print("=" * 80)
    print(" COBOL KNOWLEDGE EXTRACTION: GRAPH & SLICE-AWARE CODE RAG PIPELINE")
    print("=" * 80)

    # 1. Ingestion
    data_dir = os.path.join(BASE_DIR, "sample_data")
    src_file = os.path.join(data_dir, "loan_calc.cbl")
    st_file = os.path.join(data_dir, "symbol_table.json")
    cg_file = os.path.join(data_dir, "call_graph.json")
    ast_file = os.path.join(data_dir, "koopa_ast.json")

    print("\n[Step 1] Ingesting Koopa Parser Artifacts...")
    loader = KoopaLoader(src_file, st_file, cg_file, ast_file)
    loader.load_all()
    print(f"  ✓ Loaded Source Code: {len(loader.source_lines)} lines")
    print(f"  ✓ Loaded Symbol Table: {len(loader.symbol_table)} variables ({len(loader.condition_88_to_parent)} condition 88s)")
    print(f"  ✓ Loaded Call Graph: {len(loader.call_nodes)} nodes, {len(loader.call_edges)} edges")

    # 2. AST Chunking
    print("\n[Step 2] Chunking Procedure Division via AST Boundaries...")
    chunker = ASTChunker(loader)
    chunks = chunker.chunk_procedure_division()
    print(f"  ✓ Extracted {len(chunks)} paragraph chunks:")
    for c in chunks:
        print(f"    - Paragraph: {c.paragraph_name:<25} (Lines {c.start_line:2d}-{c.end_line:2d}) | Refs: {len(c.referenced_symbols)} symbols")

    # 3. Hybrid Index & Retrieval
    print("\n[Step 3] Initializing Hybrid Retriever...")
    retriever = HybridRetriever(chunks, loader)
    slicer = ContextSlicer(loader)
    extractor = RuleExtractor()

    test_queries = [
        "How is customer tier and credit score evaluated for loan rejection or approval?",
        "Where is the risk penalty added to total interest for unsecured collateral?"
    ]

    for q_idx, query in enumerate(test_queries, 1):
        print("\n" + "-" * 80)
        print(f"[Query {q_idx}] User asks: \"{query}\"")
        print("-" * 80)

        # Retrieve top paragraph chunk + graph expansion
        results = retriever.retrieve(query, top_k=1, expand_with_call_graph=True)
        top_chunk, score = results[0]
        print(f"  * Top Retrieved Chunk: {top_chunk.paragraph_name} (Relevance Score: {score:.2f})")

        # Context Assembly (Slice Symbol Table + Call Graph)
        assembled_context = slicer.assemble_context(top_chunk)
        print(f"  * Assembled Context: {len(assembled_context.symbol_table_slice)} variables sliced, "
              f"Callers: {assembled_context.callers}, Callees: {assembled_context.callees}")

        # Display Formatted Prompt Context for LLM
        print("\n--- [Synthesized Prompt Context Passed to LLM] ---")
        print(assembled_context.formatted_prompt_context)
        print("--------------------------------------------------")

        # Business Rule Extraction
        rule_output = extractor.extract_rules_offline(assembled_context, query)
        print("\n[Extracted Knowledge / Business Rule Metadata]:")
        print(json.dumps(rule_output, indent=2))

    # 4. Evaluation & Ablation Study
    print("\n" + "=" * 80)
    print(" [Step 4] Running Evaluation & Ablation Study (Naive RAG vs Proposed System)")
    print("=" * 80)
    evaluator = Evaluator(loader)
    ablation = evaluator.run_ablation_summary(chunks, slicer)
    print(json.dumps(ablation, indent=2))

    print("\n" + "=" * 80)
    print(" Pipeline Execution Finished Successfully.")
    print("=" * 80)

if __name__ == "__main__":
    main()
