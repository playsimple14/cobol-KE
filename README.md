# COBOL Knowledge Extraction: Graph & Slice-Aware Code RAG

A modular research codebase for legacy modernization and Business Rule Extraction (BRE) from COBOL programs using **Code RAG**, combining **Koopa ASTs**, **Symbol Tables (Data Dictionary)**, and **Call Graphs**.

---

## 1. Quick Start: How to Run

The baseline pipeline runs using standard Python 3 (Python 3.8+) with **zero external dependencies required**:

```bash
cd /Users/kevin/Desktop/free-claude
python3 run_pipeline.py
```

### What Happens When You Run It:
1. **Ingests Koopa Artifacts:** Loads the raw COBOL file, Symbol Table (with `88` condition codes and picture clauses), Call Graph (callers/callees), and AST.
2. **Performs AST Chunking:** Splits the Procedure Division at paragraph boundaries while tracking referenced symbols.
3. **Executes Hybrid Retrieval:** Runs symbol-boosted lexical & semantic retrieval for user queries, plus Call Graph expansion.
4. **Context Slicing:** Dynamically extracts *only* the relevant Working-Storage fields and 88-level conditions used in the retrieved paragraph.
5. **Generates Knowledge Extraction Prompts:** Assembles the self-contained prompt context designed for LLMs.
6. **Runs Ablation Study:** Quantitatively compares naive text RAG against structure-aware RAG on symbol grounding and condition resolution.

---

## 2. Project Structure

```text
free-claude/
├── README.md                           # This guide & paper references
├── requirements.txt                    # Optional extensions (embeddings, networkx, llm SDKs)
├── run_pipeline.py                     # Runnable end-to-end pipeline script
├── sample_data/
│   ├── loan_calc.cbl                   # Realistic COBOL program (Working-Storage, 88s, Perform)
│   ├── symbol_table.json               # Koopa Symbol Table representation
│   ├── call_graph.json                 # Koopa Call Graph representation
│   └── koopa_ast.json                  # Koopa AST representation
├── src/
│   ├── models.py                       # Data models (SymbolEntry, CodeChunk, AssembledContext)
│   ├── ingestion/
│   │   └── koopa_loader.py             # Parser output loader
│   ├── chunking/
│   │   └── ast_chunker.py              # Paragraph-level AST boundary chunker
│   ├── slicing/
│   │   └── context_slicer.py           # Symbol Table pruner & Call Graph neighborhood slicer
│   ├── retrieval/
│   │   └── hybrid_retriever.py         # BM25 + Symbol Boost + Call Graph Expansion
│   └── extraction/
│       └── rule_extractor.py           # Business Rule Extractor & Prompt Synthesizer
└── evaluation/
    └── benchmark.py                    # Ablation study: Grounding & Coverage evaluator
```

---

## 3. How to Connect Your Work Laptop COBOL & Koopa Outputs

When you transfer your manager's COBOL files and your teammate's Koopa parser outputs:
1. Replace or add your files in `sample_data/`:
   - Your COBOL source: `sample_data/<your_file>.cbl`
   - Koopa Symbol Table export: `sample_data/<your_file>_st.json`
   - Koopa Call Graph export: `sample_data/<your_file>_cg.json`
   - Koopa AST export: `sample_data/<your_file>_ast.json`
2. Update the file paths in `run_pipeline.py` (lines 31–35) and run!

---

## 4. Key Research Papers & Open-Source Codebases to Reference

To satisfy your senior's request to read the latest related work, study these open repositories:

1. **RepoAgent** (AST-based Repository Knowledge Extraction)
   - *Paper:* [RepoAgent: An LLM-Powered Open-Source Framework for Repository-level Code Documentation Generation](https://arxiv.org/abs/2402.16667)
   - *GitHub:* [https://github.com/OpenBMB/RepoAgent](https://github.com/OpenBMB/RepoAgent)
   - *Key takeaway:* How to traverse AST topological orders to generate linked documentation.

2. **RepoCoder** (Iterative Code Retrieval & Generation)
   - *Paper:* [RepoCoder: Repository-Level Code Completion Through Iterative Retrieval and Generation](https://arxiv.org/abs/2303.12570)
   - *GitHub:* [https://github.com/microsoft/RepoCoder](https://github.com/microsoft/RepoCoder)
   - *Key takeaway:* Iterative context refinement using intermediate model outputs.

3. **CodePlan** (Repository-level Planning over Dependency Graphs)
   - *Paper:* [CodePlan: Repository-level Coding using Planned Chains of Invocations](https://arxiv.org/abs/2309.12499)
   - *Key takeaway:* How to traverse call graphs and dependency graphs to supply accurate LLM context.

4. **IBM Granite for Code / Watsonx Code Assistant for Z**
   - *Paper:* [Granite Code Models: A Family of Open Foundation Models for Code Intelligence](https://arxiv.org/abs/2405.04324)
   - *GitHub / Hugging Face:* [https://github.com/ibm-granite/granite-code-models](https://github.com/ibm-granite/granite-code-models)
   - *Key takeaway:* Enterprise pre-training benchmarks on COBOL, JCL, and PL/I.

5. **Koopa COBOL Parser**
   - *GitHub:* [https://github.com/krisdejongh/koopa](https://github.com/krisdejongh/koopa)
   - *Key takeaway:* Grammar specifications, AST tree traversal, and copybook resolution.
