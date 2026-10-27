# Research Strategy: Working on Your TCS Work Laptop

## The Reality

- ✅ You have real COBOL files locally (TCS work laptop)
- ✅ You have ACAS application (real legacy system)
- ✅ You have Koopa parser results already run
- ✅ You can work with your team
- ❌ Can't transfer to personal laptop (data/security restrictions)
- ❌ This project is scaffolding/template only

**Solution: Use this repo as a TEMPLATE. Replicate the structure on your work laptop with YOUR actual data.**

---

## Phase 1: Set Up on Your Work Laptop (This Week)

### 1.1 Clone/Replicate the Template

On your **TCS work laptop**, recreate this directory structure:

```bash
cd /path/to/your/work/projects
git clone https://github.com/yourusername/free-claude.git  # or create new repo
cd free-claude

# Verify structure is there:
ls -la
# → run_pipeline.py
# → requirements.txt
# → src/ (with all modules)
# → evaluation/
# → sample_data/
```

### 1.2 Replace Sample Data with Real Data

```bash
cd /path/to/your/work/projects/free-claude/sample_data

# REMOVE toy data:
rm loan_calc.cbl symbol_table.json call_graph.json koopa_ast.json

# ADD your real COBOL files from TCS:
# Copy from your actual COBOL directories:
cp /path/to/tcs/cobol/files/ACAS/*.cbl ./
cp /path/to/tcs/koopa_results/ACAS/* ./

# Verify:
ls -lah
# You should see:
# ├── <your_program_1>.cbl
# ├── <your_program_1>_st.json     (Koopa symbol table)
# ├── <your_program_1>_cg.json     (Koopa call graph)
# ├── <your_program_1>_ast.json    (Koopa AST)
# ├── <your_program_2>.cbl
# ├── <your_program_2>_st.json
# ... etc
```

### 1.3 Update Paths in run_pipeline.py

```python
# run_pipeline.py (around line 34-38)

# BEFORE (toy data):
src_file = os.path.join(data_dir, "loan_calc.cbl")
st_file = os.path.join(data_dir, "symbol_table.json")
cg_file = os.path.join(data_dir, "call_graph.json")
ast_file = os.path.join(data_dir, "koopa_ast.json")

# AFTER (your real data):
# Choose your FIRST COBOL program as test case:
PROGRAM_NAME = "ACAS_MAIN"  # or whatever your program is called

src_file = os.path.join(data_dir, f"{PROGRAM_NAME}.cbl")
st_file = os.path.join(data_dir, f"{PROGRAM_NAME}_st.json")
cg_file = os.path.join(data_dir, f"{PROGRAM_NAME}_cg.json")
ast_file = os.path.join(data_dir, f"{PROGRAM_NAME}_ast.json")
```

### 1.4 Test the Pipeline

```bash
cd /path/to/your/work/projects/free-claude
python3 run_pipeline.py

# Expected output:
# [Step 1] Ingesting Koopa Parser Artifacts...
#   ✓ Loaded Source Code: XXXX lines
#   ✓ Loaded Symbol Table: XXX variables
#   ✓ Loaded Call Graph: XXX nodes, XXX edges
# [Step 2] Chunking Procedure Division via AST Boundaries...
#   ✓ Extracted N paragraph chunks
# [Step 3] Initializing Hybrid Retriever...
# [Query 1] User asks: "..."
#   ... context output ...
# [Step 4] Running Evaluation & Ablation Study...
```

**If it runs → You have a working baseline on real data!**

---

## Phase 2: Work with Your Team (2-3 weeks)

### 2.1 Share Code (Not Data)

```bash
# Create a shared Git repository on your TCS internal GitLab/GitHub:
# (assuming TCS has internal Git hosting or GitHub Enterprise)

cd /path/to/your/work/projects/free-claude

# Initialize or push to internal repo:
git init
git add .
git commit -m "Initial: CodeRAG pipeline template for ACAS research"
git remote add origin <TCS_INTERNAL_GIT_URL>
git push -u origin main

# Your teammates can now:
git clone <TCS_INTERNAL_GIT_URL> free-claude
cd free-claude
python3 run_pipeline.py  # Against THEIR local COBOL files
```

### 2.2 Create Team Annotation Protocol

Since you have REAL COBOL now, start annotating test queries:

```bash
# Create: sample_data/annotations.json
# This is INDEPENDENT of data — just structure + queries

cat > sample_data/annotations.json << 'EOF'
{
  "annotation_protocol": "ACAS Business Rule Extraction",
  "annotators": ["Your Name", "Teammate 1", "Teammate 2"],
  "instructions": "For each query, mark ground truth paragraphs and expected symbols",
  
  "queries": [
    {
      "query_id": "acas_001",
      "query": "How is customer eligibility determined for the loan product?",
      "annotator": "Your Name",
      "date": "2026-10-26",
      "expected_paragraphs": ["SECTION-A", "SECTION-B"],
      "expected_key_symbols": ["CUSTOMER-AGE", "CREDIT-SCORE", "ELIGIBILITY-FLAG"],
      "expected_88_conditions": [
        {"symbol": "CUSTOMER-AGE", "condition": "AGE-VALID", "range": "18-120"}
      ],
      "confidence": "high",
      "notes": "This is the first decision point in the main flow"
    },
    {
      "query_id": "acas_002",
      "query": "Where are interest rates calculated and adjusted for risk?",
      "annotator": "Teammate 1",
      "date": "2026-10-26",
      "expected_paragraphs": ["RATE-CALC", "RISK-ADJUST"],
      "expected_key_symbols": ["BASE-RATE", "RISK-PREMIUM", "FINAL-RATE"],
      "expected_88_conditions": [],
      "confidence": "high"
    }
  ]
}
EOF

# Share this file with teammates:
git add sample_data/annotations.json
git commit -m "Add ACAS annotation protocol for team evaluation"
git push
```

### 2.3 Divide Work by COBOL Program

If you have **N COBOL programs**, divide them:

```
Your Work Laptop:
├── ACAS_MAIN.cbl          ← You analyze this
├── ACAS_MODULE_1.cbl      ← Teammate A analyzes this
├── ACAS_MODULE_2.cbl      ← Teammate B analyzes this
└── ACAS_BATCH.cbl         ← Teammate C analyzes this

All results → Shared internal Git repo
```

```bash
# Each teammate runs:
python3 run_pipeline.py --program ACAS_MODULE_1

# Results go to:
results/ACAS_MODULE_1/
├── chunks.json
├── retrieval_results.json
├── evaluation_metrics.json
└── assembled_contexts.json

# Commit to shared repo:
git add results/
git commit -m "Analysis results for ACAS_MODULE_1"
git push
```

---

## Phase 3: Build Evaluation Framework (2-3 weeks)

### 3.1 Create Evaluation Script for Your Data

```python
# Create: evaluation/run_acas_evaluation.py

#!/usr/bin/env python3
"""
Evaluation script for ACAS programs using your real data.
Run this locally on work laptop, share results via Git.
"""

import os
import json
import sys
from pathlib import Path

# Add src to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.ingestion.koopa_loader import KoopaLoader
from src.chunking.ast_chunker import ASTChunker
from src.retrieval.hybrid_retriever import HybridRetriever
from src.slicing.context_slicer import ContextSlicer
from evaluation.benchmark import Evaluator

def evaluate_program(program_name, data_dir="sample_data"):
    """
    Evaluate a single COBOL program against annotated queries.
    """
    print(f"\n{'='*80}")
    print(f"Evaluating Program: {program_name}")
    print(f"{'='*80}")
    
    # Load real Koopa outputs
    src_file = os.path.join(data_dir, f"{program_name}.cbl")
    st_file = os.path.join(data_dir, f"{program_name}_st.json")
    cg_file = os.path.join(data_dir, f"{program_name}_cg.json")
    ast_file = os.path.join(data_dir, f"{program_name}_ast.json")
    
    # Verify files exist
    for f in [src_file, st_file, cg_file, ast_file]:
        if not os.path.exists(f):
            print(f"ERROR: Missing {f}")
            return None
    
    # Load & process
    print(f"[1] Loading Koopa artifacts...")
    loader = KoopaLoader(src_file, st_file, cg_file, ast_file)
    loader.load_all()
    print(f"  ✓ {len(loader.source_lines)} lines, {len(loader.symbol_table)} symbols")
    
    print(f"[2] Chunking AST...")
    chunker = ASTChunker(loader)
    chunks = chunker.chunk_procedure_division()
    print(f"  ✓ {len(chunks)} paragraph chunks")
    
    print(f"[3] Running retrieval evaluation...")
    retriever = HybridRetriever(chunks, loader)
    slicer = ContextSlicer(loader)
    evaluator = Evaluator(loader)
    
    # Load annotations
    annotations_file = os.path.join(data_dir, "annotations.json")
    if not os.path.exists(annotations_file):
        print(f"WARNING: No annotations.json found. Skipping evaluation.")
        return chunks
    
    with open(annotations_file) as f:
        annotations = json.load(f)
    
    # Evaluate against annotations
    results = {
        "program": program_name,
        "timestamp": "2026-10-26",
        "statistics": {
            "total_paragraphs": len(chunks),
            "total_symbols": len(loader.symbol_table),
            "total_88_conditions": len(loader.condition_88_to_parent)
        },
        "queries": []
    }
    
    for query_obj in annotations.get("queries", []):
        query = query_obj["query"]
        expected_paragraphs = set(query_obj.get("expected_paragraphs", []))
        expected_symbols = set(query_obj.get("expected_key_symbols", []))
        
        print(f"\n  Query: {query[:60]}...")
        
        # Retrieve
        retrieved = retriever.retrieve(query, top_k=3, expand_with_call_graph=True)
        retrieved_paragraphs = {r[0].paragraph_name for r in retrieved}
        retrieved_symbols = {sym for r in retrieved for sym in r[0].referenced_symbols}
        
        # Score
        precision = len(retrieved_paragraphs & expected_paragraphs) / len(retrieved_paragraphs) if retrieved_paragraphs else 0
        recall = len(retrieved_paragraphs & expected_paragraphs) / len(expected_paragraphs) if expected_paragraphs else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        symbol_coverage = len(retrieved_symbols & expected_symbols) / len(expected_symbols) if expected_symbols else 0
        
        results["queries"].append({
            "query_id": query_obj["query_id"],
            "query": query,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "symbol_coverage": round(symbol_coverage, 3),
            "retrieved_paragraphs": list(retrieved_paragraphs),
            "expected_paragraphs": list(expected_paragraphs)
        })
        
        print(f"    Precision: {precision:.2%}, Recall: {recall:.2%}, F1: {f1:.2%}")
    
    # Save results
    results_dir = os.path.join(BASE_DIR, "results", program_name)
    os.makedirs(results_dir, exist_ok=True)
    
    results_file = os.path.join(results_dir, "evaluation.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {results_file}")
    return results

if __name__ == "__main__":
    # Evaluate all ACAS programs
    programs = ["ACAS_MAIN", "ACAS_MODULE_1", "ACAS_MODULE_2"]  # Update with YOUR program names
    
    all_results = {}
    for prog in programs:
        result = evaluate_program(prog)
        if result:
            all_results[prog] = result
    
    # Summary
    print(f"\n{'='*80}")
    print("EVALUATION SUMMARY")
    print(f"{'='*80}")
    for prog, result in all_results.items():
        if isinstance(result, dict) and "queries" in result:
            avg_f1 = sum(q["f1"] for q in result["queries"]) / len(result["queries"])
            print(f"{prog}: Average F1 = {avg_f1:.2%}")
```

Run this:
```bash
cd /path/to/work/projects/free-claude
python3 evaluation/run_acas_evaluation.py

# Output:
# ================================================================================
# Evaluating Program: ACAS_MAIN
# ================================================================================
# [1] Loading Koopa artifacts...
#   ✓ 5432 lines, 187 symbols
# [2] Chunking AST...
#   ✓ 42 paragraph chunks
# [3] Running retrieval evaluation...
#   Query: How is customer eligibility determined...
#     Precision: 85.00%, Recall: 90.00%, F1: 87.50%
#   ... more queries ...
```

### 3.2 Create Comparison Report

```python
# Create: evaluation/generate_report.py

import json
import os
from pathlib import Path

def generate_comparison_report():
    """Generate markdown report comparing all programs."""
    
    results_dir = Path("results")
    report = []
    report.append("# ACAS CodeRAG Evaluation Report\n")
    report.append("## Summary\n")
    
    # Table of all programs
    report.append("| Program | Avg F1 | Symbol Coverage | Paragraphs | Symbols |\n")
    report.append("|---------|--------|-----------------|-----------|----------|\n")
    
    for prog_dir in sorted(results_dir.iterdir()):
        if prog_dir.is_dir():
            eval_file = prog_dir / "evaluation.json"
            if eval_file.exists():
                with open(eval_file) as f:
                    data = json.load(f)
                
                avg_f1 = sum(q["f1"] for q in data["queries"]) / len(data["queries"])
                avg_sym_cov = sum(q["symbol_coverage"] for q in data["queries"]) / len(data["queries"])
                
                report.append(f"| {prog_dir.name} | {avg_f1:.2%} | {avg_sym_cov:.2%} | "
                             f"{data['statistics']['total_paragraphs']} | "
                             f"{data['statistics']['total_symbols']} |\n")
    
    # Detailed per-query breakdown
    report.append("\n## Detailed Results\n")
    
    for prog_dir in sorted(results_dir.iterdir()):
        if prog_dir.is_dir():
            eval_file = prog_dir / "evaluation.json"
            if eval_file.exists():
                with open(eval_file) as f:
                    data = json.load(f)
                
                report.append(f"\n### {prog_dir.name}\n")
                for query in data["queries"]:
                    report.append(f"\n**Q{query['query_id']}:** {query['query']}\n")
                    report.append(f"- F1: {query['f1']:.2%}\n")
                    report.append(f"- Symbol Coverage: {query['symbol_coverage']:.2%}\n")
    
    # Write report
    with open("results/EVALUATION_REPORT.md", "w") as f:
        f.write("".join(report))
    
    print("✓ Report generated: results/EVALUATION_REPORT.md")

if __name__ == "__main__":
    generate_comparison_report()
```

Run:
```bash
python3 evaluation/generate_report.py
# Output: results/EVALUATION_REPORT.md with all metrics
```

---

## Phase 4: Team Collaboration (Ongoing)

### 4.1 Shared Git Workflow

```bash
# Week 1-2: Each teammate analyzes their program
# On your individual work laptops:

git pull origin main  # Get latest template
python3 evaluation/run_acas_evaluation.py
git add results/
git commit -m "Analysis: ACAS_MAIN evaluation results"
git push origin main

# Week 3: Sync up
git pull origin main  # Get all teammates' results
python3 evaluation/generate_report.py  # Aggregate all results
```

### 4.2 Team Meeting Notes

```markdown
# ACAS CodeRAG Research - Team Meeting Notes

## Objective
Extract business rules from ACAS application using structure-aware CodeRAG

## Baseline Data
- COBOL Programs: 4 (ACAS_MAIN, MODULE_1, MODULE_2, BATCH)
- Total Paragraphs: 120+
- Total Symbols: 400+
- Koopa Parser: Already run

## Current Results (Week 1)
| Program       | F1 Score | Symbol Coverage | Status |
|---------------|----------|-----------------|--------|
| ACAS_MAIN     | 87.5%    | 92%             | ✓ Done |
| ACAS_MODULE_1 | 84.2%    | 88%             | In Progress |
| ACAS_MODULE_2 | TBD      | TBD             | Pending |

## Next Steps
1. Complete evaluation for all 4 programs
2. Conduct human evaluation (inter-rater agreement)
3. Draft paper introduction & methodology
4. Target venue: EMNLP 2027 (Nov submission)
```

---

## Phase 5: Publication Prep (4-5 weeks)

### 5.1 On Work Laptop, Create Paper Structure

```bash
# Create: paper/
mkdir -p paper/figures paper/tables paper/sections

# paper/paper.md (main paper)
# paper/sections/01_introduction.md
# paper/sections/02_relatedwork.md
# paper/sections/03_approach.md
# paper/sections/04_evaluation.md
# paper/sections/05_results.md

# paper/figures/ (generated from your data)
# ├── retrieval_comparison.png
# ├── symbol_coverage_by_program.png
# └── ablation_results.png

# paper/tables/
# ├── results_summary.tex
# └── baseline_comparison.tex
```

### 5.2 Generate Results Directly from Your Data

```python
# Create: evaluation/generate_paper_tables.py

import json
from pathlib import Path

def generate_results_table():
    """Generate LaTeX table of results for paper."""
    
    results_dir = Path("results")
    
    latex = r"""
\begin{table}[h]
\centering
\caption{CodeRAG Evaluation Results on ACAS Application}
\begin{tabular}{lcccc}
\toprule
Program & F1 Score & Precision & Recall & Symbol Coverage \\
\midrule
"""
    
    for prog_dir in sorted(results_dir.iterdir()):
        if prog_dir.is_dir():
            eval_file = prog_dir / "evaluation.json"
            if eval_file.exists():
                with open(eval_file) as f:
                    data = json.load(f)
                
                avg_f1 = sum(q["f1"] for q in data["queries"]) / len(data["queries"])
                avg_prec = sum(q["precision"] for q in data["queries"]) / len(data["queries"])
                avg_recall = sum(q["recall"] for q in data["queries"]) / len(data["queries"])
                avg_sym = sum(q["symbol_coverage"] for q in data["queries"]) / len(data["queries"])
                
                latex += f"{prog_dir.name} & {avg_f1:.1%} & {avg_prec:.1%} & {avg_recall:.1%} & {avg_sym:.1%} \\\\\n"
    
    latex += r"""
\bottomrule
\end{tabular}
\end{table}
"""
    
    with open("paper/tables/results_summary.tex", "w") as f:
        f.write(latex)
    
    print("✓ Generated: paper/tables/results_summary.tex")

if __name__ == "__main__":
    generate_results_table()
```

---

## Phase 6: Practical Tips for Your Team

### 6.1 Overcome Data Transfer Limitations

**Problem:** "I can't move COBOL files between work & personal laptop"

**Solution:** Work ONLY on work laptop. Use these tools:

```bash
# 1. Share code via Git (no data):
cd /path/to/work/projects
git init free-claude-research
cd free-claude-research
git remote add origin <TCS_INTERNAL_GIT>
git push -u origin main
# Teammates: git clone <URL> → They use their LOCAL COBOL files

# 2. Share results (not raw files):
# results/ACAS_MAIN/
# ├── evaluation.json       (safe to share - metrics only)
# ├── evaluation_report.md  (share with team)
# └── paper_figures.png     (safe to share - visuals)

# 3. Use symbolic links (if COBOL files are on shared drive):
ln -s /shared/cobol/files /path/to/work/projects/free-claude/sample_data
# Now pipeline reads from shared source, no copy needed
```

### 6.2 Set Up for Multiple Team Members

```bash
# Create: TEAM_SETUP.md

# Each teammate:
git clone <TCS_INTERNAL_GIT> free-claude
cd free-claude

# Point to YOUR local COBOL files:
ln -s /your/local/cobol/path ./sample_data

# Run pipeline:
python3 run_pipeline.py

# Push results to shared repo:
git add results/
git commit -m "Analysis: <YOUR_PROGRAM>"
git push origin main
```

### 6.3 CI/CD on Work Laptop (Local Testing)

```bash
# Create: scripts/test_locally.sh

#!/bin/bash
# Run tests before pushing to team repo

cd /path/to/work/projects/free-claude

# Test 1: Can pipeline load all COBOL files?
python3 -c "from src.ingestion.koopa_loader import KoopaLoader; print('✓ Loader imports OK')"

# Test 2: Run on each program
for program in ACAS_MAIN ACAS_MODULE_1; do
    echo "Testing $program..."
    python3 evaluation/run_acas_evaluation.py --program $program || exit 1
done

# Test 3: Generate report
python3 evaluation/generate_report.py

echo "✓ All tests passed. Safe to push."
```

---

## Putting It All Together: Your Work Laptop Workflow

### Week 1: Setup & Individual Analysis
```bash
# Your work laptop
cd ~/projects
git clone <TCS_INTERNAL_GIT> free-claude
cd free-claude

# Link your ACAS files
ln -s /your/cobol/path ./sample_data

# Test pipeline on your main program
python3 run_pipeline.py

# Analyze your program
python3 evaluation/run_acas_evaluation.py --program ACAS_MAIN

# Commit & push results
git add results/
git commit -m "Analysis: ACAS_MAIN - 87.5% F1 on test queries"
git push origin main
```

### Week 2-3: Team Collaboration
```bash
# Pull teammates' results
git pull origin main

# Review their analyses
cat results/ACAS_MODULE_1/evaluation.json

# Generate team report
python3 evaluation/generate_report.py

# Summary table: results/EVALUATION_REPORT.md
```

### Week 4-5: Paper Writing
```bash
# Generate paper tables & figures
python3 evaluation/generate_paper_tables.py
python3 evaluation/generate_paper_figures.py

# Write on work laptop (paper/ directory)
cd paper
# Start with: sections/01_introduction.md
# Edit locally, add LaTeX tables from evaluation/

# Share paper draft via internal Git (or email .docx)
```

---

## Key Advantages of Work Laptop Approach

✅ **No data transfer:** All COBOL stays on work systems  
✅ **Secure:** No personal laptops involved  
✅ **Team collaboration:** Shared Git repo with results  
✅ **Reproducible:** Every team member runs same pipeline  
✅ **Publication-ready:** Code is already sanitized (no secrets)  
✅ **Scalable:** Add more programs/team members easily  

---

## IMMEDIATE ACTION PLAN

### This Week (Oct 26-31)
- [ ] Clone free-claude repo to your work laptop
- [ ] Replace sample_data/ with your ACAS programs + Koopa outputs
- [ ] Update run_pipeline.py with your program names
- [ ] Test: `python3 run_pipeline.py` succeeds
- [ ] Create sample_data/annotations.json with 5 test queries
- [ ] Create results/ACAS_MAIN/evaluation.json

### Next Week (Nov 2-8)
- [ ] Set up internal Git repo for team
- [ ] Add teammates to repo
- [ ] Each teammate completes individual program analysis
- [ ] Pull all results → Generate team report
- [ ] Schedule team meeting to discuss findings

### Weeks 3-4 (Nov 9-22)
- [ ] Conduct human evaluation (inter-rater agreement)
- [ ] Implement 3 baseline retrievers
- [ ] Run full ablation study
- [ ] Generate paper tables & figures

### Weeks 5-8 (Nov 25 - Dec 20)
- [ ] Draft paper sections
- [ ] Submit to EMNLP 2027 (typical deadline: Nov/Dec)

---

## Questions for Your Team

Before you start, clarify with your manager/instructor:

1. **Data**: Can you store Koopa outputs on work laptop?
2. **Publication**: Are you allowed to publish research on ACAS (or anonymize it)?
3. **Team size**: How many people can contribute?
4. **Timeline**: When is deadline for paper submission?
5. **Venue**: Are there preferred conferences/journals?
6. **IP**: Does TCS retain publication rights, or can you publish independently?

**Typical answers:**
- Data: Yes, all work laptop
- Publication: Anonymize company/application name
- Team: 2-4 people (you + teammates)
- Timeline: 4-5 months (target EMNLP 2027)
- Venue: Prioritize EMNLP/ACL/ICSE
- IP: Co-authorship with TCS team

---

## Final Note: From Personal to Team Research

This personal laptop project **is NOT your final research**. It's a **template & proof-of-concept**.

Your **real research happens on your work laptop with your team**:
- Real COBOL (ACAS application)
- Real Koopa parser outputs
- Real domain experts (your team)
- Real business impact (ACAS modernization)

Use this template to **jump-start** your team's work. Then customize it for your specific COBOL programs.

Good luck with the team collaboration! 🚀
