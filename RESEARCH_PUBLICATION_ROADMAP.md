# Research Publication Roadmap: Triple-Source CodeRAG for COBOL

## Executive Summary

Your project implements a **structure-aware Code RAG** combining AST boundaries, Symbol Tables, and Call Graphs for COBOL knowledge extraction. To publish this as research, you need to strengthen **5 critical dimensions**: evaluation rigor, dataset diversity, baseline comparisons, reproducibility, and paper positioning.

---

## 1. EVALUATION RIGOR (Currently: Partial)

### Current State
- ✅ Basic ablation framework exists (`evaluation/benchmark.py`)
- ❌ No ground truth annotations
- ❌ No human evaluation metrics
- ❌ Limited quantitative metrics

### What You Need to Add

#### 1.1 Create Annotated Benchmark Dataset
**Time: 2-3 weeks | Priority: CRITICAL**

Create a **gold standard** evaluation set with manual annotations:

```python
# Create: sample_data/annotations.json
{
  "queries": [
    {
      "id": "q001",
      "query": "How is customer tier evaluated for loan rejection?",
      "paragraphs_to_retrieve": ["1000-EVAL-CUSTOMER-TIER"],  # Ground truth
      "expected_symbols": ["CREDIT-POOR", "CREDIT-GOOD", "CREDIT-EXCELLENT", "LOAN-REJECTED"],
      "expected_conditions_88": [
        {"name": "CREDIT-POOR", "range": "000-599"},
        {"name": "CREDIT-GOOD", "range": "600-749"},
        {"name": "CREDIT-EXCELLENT", "range": "750-800"}
      ],
      "expected_call_context": {
        "callers": ["0000-MAIN-PROCESS"],
        "callees": ["2000-CALC-INTEREST", "3000-APPLY-RISK-PENALTY"]
      }
    },
    {
      "id": "q002",
      "query": "Where is the risk penalty added to the interest calculation?",
      "paragraphs_to_retrieve": ["2000-CALC-INTEREST"],
      "expected_symbols": ["WS-RISK-PREMIUM", "WS-BASE-INTEREST-RATE", "WS-FINAL-INTEREST-RATE"],
      "expected_conditions_88": []
    }
  ]
}
```

**Why this matters:**
- Reviewers will demand ground truth to validate ablation claims
- Enables Precision@k, Recall@k metrics (standard in IR research)
- Quantifies improvement: "60% → 94% symbol grounding accuracy"

#### 1.2 Implement Quantitative Metrics
Add to `evaluation/benchmark.py`:

```python
class RigorousEvaluator:
    """Implements standard IR evaluation metrics."""
    
    def precision_at_k(self, retrieved_symbols, expected_symbols, k=5):
        """Precision: correct symbols in top-k / k"""
        return len(set(retrieved_symbols[:k]) & set(expected_symbols)) / k
    
    def recall_at_k(self, retrieved_symbols, expected_symbols, k=5):
        """Recall: correct symbols in top-k / all expected"""
        return len(set(retrieved_symbols[:k]) & set(expected_symbols)) / len(expected_symbols)
    
    def ndcg_at_k(self, ranked_paragraphs, expected_paragraphs, k=5):
        """Normalized Discounted Cumulative Gain - standard ranking metric"""
        dcg = sum(
            (1.0 if p in expected_paragraphs else 0.0) / math.log2(i+2)
            for i, p in enumerate(ranked_paragraphs[:k])
        )
        ideal_dcg = sum(
            1.0 / math.log2(i+2) for i in range(min(k, len(expected_paragraphs)))
        )
        return dcg / ideal_dcg if ideal_dcg > 0 else 0.0
    
    def f1_symbol_coverage(self, retrieved_symbols, expected_symbols):
        """F1 score on symbol resolution"""
        precision = len(set(retrieved_symbols) & set(expected_symbols)) / len(retrieved_symbols)
        recall = len(set(retrieved_symbols) & set(expected_symbols)) / len(expected_symbols)
        return 2 * (precision * recall) / (precision + recall)
```

#### 1.3 Human Evaluation Protocol
**Time: 1-2 weeks | Participants: 3+ COBOL experts**

```python
# Create: evaluation/human_eval.md
Human Evaluation Protocol:
1. **Instruction Clarity** (does the assembled context make sense?)
   - Scale: 1-5 Likert
   - Expected: >4.2 mean for structure-aware RAG
   
2. **Symbol Grounding Accuracy** (are data types/ranges correctly explained?)
   - Scale: Binary (yes/no per symbol)
   - Expected: >90% for structure-aware, <30% for naive RAG
   
3. **Business Logic Comprehension** (can domain expert extract rule from context?)
   - Scale: 1-5 Likert (1=impossible, 5=trivial)
   - Expected: >3.5 improvement over baseline
   
4. **Completeness** (is all necessary call context present?)
   - Scale: 1-5 Likert
   - Expected: Structure-aware should score 4.5+ vs baseline 2.0

Annotation Tool: Use Argilla/Label Studio for inter-rater agreement (Cohen's kappa > 0.7)
```

---

## 2. DATASET DIVERSITY (Currently: 1 toy example)

### Current State
- ❌ Only 1 COBOL program (loan_calc.cbl)
- ❌ Only 4 paragraphs
- ❌ Toy-sized symbol table

### What You Need to Add

#### 2.1 Curate Real-World Dataset
**Time: 3-4 weeks | Source: Open-source COBOL repositories**

Create **3-5 realistic programs** of varying complexity:

```
sample_data/
├── loan_calc.cbl                    (current: 100 lines, 4 paragraphs)
├── batch_processor.cbl              (NEW: 500 lines, 15 paragraphs) 
├── payroll_calc.cbl                 (NEW: 800 lines, 25 paragraphs)
├── inventory_mgmt.cbl               (NEW: 400 lines, 12 paragraphs)
└── complex_ledger.cbl               (NEW: 1200 lines, 40+ paragraphs)

# Plus parser outputs for each:
├── batch_processor_st.json          (Symbol Table)
├── batch_processor_cg.json          (Call Graph)
├── batch_processor_ast.json         (AST)
# ... etc
```

**Sources to find real COBOL:**
1. **GitHub GnuCOBOL examples**: `github.com/GnuCOBOL/gnucobol/tree/master/test`
2. **Open COBOL repositories**: Search "COBOL" on GitHub (filter by >500 stars)
3. **IBM z/OS samples** (if accessible to you)
4. **Legacy modernization case studies** (academic papers often include samples)

**Dataset Statistics to report:**
```markdown
| Program          | LOC  | Paragraphs | Symbols | 88-Conditions | Call Edges |
|------------------|------|-----------|---------|---------------|-----------|
| loan_calc.cbl    | 100  | 4         | 13      | 6             | 4         |
| batch_processor  | 500  | 15        | 45      | 12            | 18        |
| payroll_calc     | 800  | 25        | 67      | 20            | 31        |
| inventory_mgmt   | 400  | 12        | 52      | 8             | 14        |
| complex_ledger   | 1200 | 40        | 120     | 35            | 62        |
| **Total**        | 3000 | 96        | 297     | 81            | 129       |
```

#### 2.2 Create Test Query Collections
**Time: 1 week**

For each program, craft **5-10 realistic queries** covering:
- Symbol resolution queries: "What are the valid credit score ranges?"
- Business logic queries: "How is the tax deduction calculated?"
- Data lineage queries: "Where is EMPLOYEE-NAME used in the payroll system?"
- Control flow queries: "What happens after the VALIDATION paragraph?"

```python
# Create: sample_data/query_collections.json
{
  "batch_processor": [
    {
      "query_id": "bp_001",
      "query": "Explain the batch validation process for incoming records",
      "query_type": "business_logic",
      "relevant_paragraphs": ["100-VALIDATE-RECORD", "200-BUILD-ERROR-LOG"],
      "expected_key_symbols": ["INPUT-RECORD", "VALIDATION-ERROR-FLAG"]
    },
    {
      "query_id": "bp_002",
      "query": "How are rejected batches handled?",
      "query_type": "control_flow",
      "relevant_paragraphs": ["500-REJECT-BATCH", "600-LOG-REJECTION"]
    }
  ]
}
```

---

## 3. BASELINE COMPARISONS (Currently: Naive vs Proposed only)

### Current State
- ✅ Naive token RAG baseline exists
- ❌ Missing: industry-standard retrieval baselines
- ❌ Missing: LLM + CodeRAG comparisons
- ❌ Missing: Semantic search baseline

### What You Need to Add

#### 3.1 Implement Standard Baselines
Add to `evaluation/benchmark.py`:

```python
class BaselineRetriever:
    """Standard IR and code retrieval baselines for comparison."""
    
    def baseline_1_random(self, queries, top_k=1):
        """Random paragraph selection (true baseline)."""
        return random.sample(self.chunks, top_k)
    
    def baseline_2_bm25_only(self, query, top_k=1):
        """Pure lexical BM25 (no symbols, no graph)."""
        # Already in your hybrid_retriever.py - extract it
        pass
    
    def baseline_3_semantic_bm25(self, query, top_k=1):
        """BM25 + basic semantic similarity (no symbol table)."""
        # Requires embeddings (optional dependency)
        embeddings = self.get_embeddings(query)
        semantic_scores = [cosine_similarity(embeddings, chunk) for chunk in self.chunks]
        lexical_scores = [self.bm25_score(query, i) for i in range(len(self.chunks))]
        combined = [0.5 * lex + 0.5 * sem for lex, sem in zip(lexical_scores, semantic_scores)]
        return sorted(enumerate(combined), key=lambda x: -x[1])[:top_k]
    
    def baseline_4_ast_only(self, query, top_k=1):
        """AST chunking but NO symbol table slicing, no call graph."""
        pass
    
    def baseline_5_proposed_full(self, query, top_k=1):
        """YOUR method: AST + Symbol Table + Call Graph."""
        pass

# Expected results table for paper:
# | Baseline                      | NDCG@1 | Precision@1 | Symbol Coverage | 88-Condition Resolution |
# |-------------------------------|--------|-------------|-----------------|------------------------|
# | 1. Random                     | 0.00   | 0%          | 0%              | 0%                     |
# | 2. BM25 Only                  | 0.45   | 45%         | 12%             | 0%                     |
# | 3. BM25 + Semantic            | 0.52   | 52%         | 25%             | 0%                     |
# | 4. AST Only (no slicing)      | 0.61   | 61%         | 40%             | 0%                     |
# | 5. **Proposed (Full)**        | **0.89** | **89%**     | **94%**         | **100%**               |
```

#### 3.2 Add LLM-in-the-Loop Evaluation
**Optional but valuable for SOTA positioning:**

```python
class LLMEvaluator:
    """Evaluate assembled context quality via Claude API."""
    
    def evaluate_context_quality(self, assembled_context, ground_truth_rules):
        """
        Ask Claude: "Given this context, extract the business rule.
        Compare your extraction to the ground truth. Rate accuracy 1-5."
        """
        pass
    
    def compare_llm_performance(self, query):
        """
        Run same query with:
        - LLM + Naive RAG context
        - LLM + Proposed RAG context
        Compare outputs for hallucination rate, grounding accuracy
        """
        pass
```

---

## 4. REPRODUCIBILITY & CODE QUALITY

### Current State
- ✅ Zero external dependencies (good!)
- ✅ Clear module structure
- ❌ Missing: requirements.txt with optional extras
- ❌ Missing: Unit tests
- ❌ Missing: CI/CD pipeline
- ❌ Missing: Detailed docstrings
- ❌ Missing: Type hints

### What You Need to Add

#### 4.1 Create requirements.txt with Extras
```txt
# requirements.txt
# Core (zero dependencies - already working)
# No mandatory deps

# Optional: For semantic search
[extras] embeddings
sentence-transformers>=2.2.0
numpy>=1.21.0

# Optional: For visualization & benchmarking
[extras] viz
matplotlib>=3.5.0
seaborn>=0.12.0

# Optional: For LLM integration
[extras] llm
anthropic>=0.20.0
openai>=1.0.0

# Dev: For testing & docs
[extras] dev
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
mypy>=1.0.0
sphinx>=5.0.0
```

#### 4.2 Add Comprehensive Unit Tests
```python
# tests/test_retrieval.py
import pytest
from src.retrieval.hybrid_retriever import HybridRetriever
from src.models import CodeChunk

class TestHybridRetriever:
    @pytest.fixture
    def retriever(self, sample_chunks, sample_loader):
        return HybridRetriever(sample_chunks, sample_loader)
    
    def test_bm25_retrieval(self, retriever):
        """Test BM25 scoring on known queries."""
        results = retriever.retrieve("interest calculation", top_k=1)
        assert len(results) == 1
        assert results[0][0].paragraph_name == "2000-CALC-INTEREST"
    
    def test_symbol_boosting(self, retriever):
        """Test that symbol-heavy queries get boosted."""
        # Query with symbol names should rank higher than generic queries
        symbol_query_score = retriever.retrieve("WS-FINAL-INTEREST-RATE", top_k=1)[0][1]
        generic_query_score = retriever.retrieve("rate", top_k=1)[0][1]
        assert symbol_query_score > generic_query_score
    
    def test_call_graph_expansion(self, retriever):
        """Test that call graph neighbors are included."""
        results = retriever.retrieve("evaluate tier", expand_with_call_graph=True, top_k=5)
        paragraph_names = [r[0].paragraph_name for r in results]
        # Should include both callers and callees
        assert "0000-MAIN-PROCESS" in paragraph_names or "2000-CALC-INTEREST" in paragraph_names

# Run: pytest -v tests/ --cov=src/
```

#### 4.3 Add Type Hints & Docstrings
```python
# Example: Enhanced src/models.py
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class SymbolEntry:
    """
    Represents a single symbol in the COBOL symbol table (data dictionary).
    
    Attributes:
        name: Variable name (e.g., "WS-FINAL-INTEREST-RATE")
        level: COBOL level number (01, 05, 88)
        pic: Picture clause defining data type/size (e.g., "9(3)V99")
        section: Division section name (e.g., "WORKING-STORAGE SECTION")
        parent: Parent group variable if nested
        default: Initial value
        condition_88s: List of 88-level condition definitions
        redefines: Variable that this symbol redefines
    
    Example:
        >>> symbol = SymbolEntry(
        ...     name="WS-CREDIT-SCORE",
        ...     level="01",
        ...     pic="9(3)",
        ...     condition_88s=[
        ...         {"name": "CREDIT-POOR", "range": "000-599"},
        ...         {"name": "CREDIT-GOOD", "range": "600-749"}
        ...     ]
        ... )
    """
    name: str
    level: str
    pic: Optional[str] = None
    section: str = "WORKING-STORAGE"
    parent: Optional[str] = None
    default: Optional[str] = None
    condition_88s: List[Dict[str, str]] = field(default_factory=list)
    redefines: Optional[str] = None
```

#### 4.4 Create GitHub Actions CI/CD
```yaml
# .github/workflows/test.yml
name: Tests & Linting

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Lint with black & mypy
      run: |
        black --check src/ tests/
        mypy src/ --ignore-missing-imports
    
    - name: Run tests with coverage
      run: pytest tests/ --cov=src/ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 5. PAPER POSITIONING & WRITING

### Current State
- ❌ No written paper
- ❌ No clear positioning vs. related work
- ❌ No contribution statement

### What You Need to Write

#### 5.1 Paper Structure (15-20 pages for top venue)

```markdown
# Title
"Triple-Source Code RAG: Leveraging AST, Symbol Tables, and Call Graphs 
for COBOL Business Rule Extraction"

## 1. Introduction (2 pages)
- Problem: Legacy COBOL systems hard to modernize
- Naive RAG doesn't work: no semantic grounding
- Your insight: Structured parser outputs enable grounding
- Contribution: Triple-source CodeRAG + ablation study

## 2. Related Work (2-3 pages)
- Code RAG methods (RepoAgent, RepoCoder, CodePlan)
- COBOL-specific work (IBM Granite, Watsonx)
- Program understanding (symbol tables, call graphs, data flow)
- **Position yourself**: "First to combine all three for COBOL"

## 3. Approach (3-4 pages)
- Koopa parser architecture
- AST chunking strategy (why paragraph boundaries?)
- Symbol table slicing algorithm
- Call graph expansion (1-hop vs multi-hop)
- Hybrid retrieval scoring formula

## 4. Evaluation (4-5 pages)
- **Datasets**: Describe your 3-5 COBOL programs
- **Metrics**: NDCG, Precision@k, Symbol Coverage, Condition Resolution
- **Baselines**: 5 baselines as described above
- **Results**: Tables showing 60%→94% improvements
- **Human evaluation**: Inter-rater agreement, qualitative feedback

## 5. Results & Discussion (2-3 pages)
- What worked well
- Error analysis: where does your method fail?
- Limitations: only handles PERFORM/GOTO, not CALL
- Future work

## 6. Reproducibility (1 page)
- GitHub link (make it public!)
- Docker container for Koopa setup
- How to extract parser outputs
- How to extend to other programs

## 7. Appendix
- Full tables of results
- Query examples
- Annotation guidelines for human eval
- Sample assembled contexts
```

#### 5.2 Key Claims to Validate
Before submission, ensure you can defend these with data:

1. **"Symbol-aware retrieval improves grounding from X% to Y%"**
   - Need: Quantitative metric + statistical significance test

2. **"88-level conditions require explicit context slicing"**
   - Need: Error analysis showing naive RAG misses conditions

3. **"Call graph expansion is necessary for complete context"**
   - Need: Examples where 1-hop expansion prevents hallucination

4. **"Paragraph boundaries are better than token-level chunking"**
   - Need: Comparison of chunk quality metrics

5. **"COBOL knowledge extraction accelerates modernization"**
   - Nice to have: Case study or user study showing time savings

#### 5.3 Related Work Table for Paper
```markdown
| Method            | AST Aware | Symbol Table | Call Graph | COBOL Specific | Open Source |
|-------------------|-----------|--------------|------------|----------------|-------------|
| RepoAgent         | ✓         | ✗            | ✓          | ✗              | ✓           |
| RepoCoder         | ✓         | ✗            | ✗          | ✗              | ✓           |
| CodePlan          | ✓         | ✓            | ✓          | ✗              | ✓           |
| IBM Granite       | ✓         | ✓            | ?          | ✓              | ✗           |
| **This Work**     | **✓**     | **✓**        | **✓**      | **✓**          | **✓**       |
```

---

## 6. IMPLEMENTATION TIMELINE

### Phase 1: Foundation (2-3 weeks)
- [ ] Add ground truth annotations (sample_data/annotations.json)
- [ ] Implement rigorous metrics (evaluation/benchmark.py)
- [ ] Add type hints & docstrings to all modules
- [ ] Create unit tests (tests/)

### Phase 2: Expansion (3-4 weeks)
- [ ] Curate 3-5 real COBOL programs
- [ ] Extract Koopa parser outputs for each
- [ ] Create query collections (sample_data/query_collections.json)
- [ ] Implement 5 baseline retrievers

### Phase 3: Evaluation (2-3 weeks)
- [ ] Run full ablation study
- [ ] Conduct human evaluation (recruit 3-5 COBOL experts)
- [ ] Compute inter-rater agreement
- [ ] Generate results tables

### Phase 4: Reproducibility (1-2 weeks)
- [ ] Add requirements.txt with extras
- [ ] Create GitHub Actions CI/CD
- [ ] Make repo public + add comprehensive README
- [ ] Publish on arXiv if desired

### Phase 5: Paper Writing (3-4 weeks)
- [ ] Write first draft (core contributions)
- [ ] Iterate with co-authors/advisors
- [ ] Prepare camera-ready version
- [ ] Submit to target venue

**Total: ~4-5 months to publication-ready**

---

## 7. TARGET VENUES

### Tier-1 (SOTA research)
- **ACL/EMNLP**: Natural language processing
- **ICSE/FSE**: Software engineering
- **PLDI**: Programming languages
- **NeurIPS/ICML**: Machine learning (if novel learning component)

### Tier-2 (Strong domain + ML)
- **ASE**: Automated software engineering
- **MSR**: Mining software repositories
- **SANER**: Software analysis & reengineering
- **SCAM**: Source code analysis & manipulation

### Tier-3 (Specialized/Industry)
- **CASCON**: IBM conference on systems & software
- **Legacy Systems Workshop** (at ICSE/FSE)
- **Modernization Track** (specialized venues)

**Recommendation: Target EMNLP or ACL first** (your contribution is strong on NLP+code understanding side). If rejected, ICSE/FSE next (software engineering focus).

---

## 8. QUICK WINS (Do These First)

Pick the 3 highest-impact items if time is limited:

1. **Add quantitative metrics** (1 week)
   - Implement Precision@k, Recall@k, NDCG, F1
   - Run on sample data
   - Shows immediate improvement over naive RAG

2. **Create annotated benchmark** (1-2 weeks)
   - Hand-annotate 10-15 queries for loan_calc.cbl
   - Enables validation of your ablation claims
   - Reviewers will demand this

3. **Implement 3 baselines** (1-2 weeks)
   - Random, BM25-only, AST-only
   - Run on benchmark queries
   - Build convincing results table

**These three items alone get you 80% of the way to "publication ready."**

---

## 9. COMMON PITFALLS TO AVOID

- ❌ **No ground truth:** Claiming improvement without annotated test set
- ❌ **Cherry-picked examples:** Show average performance, not best cases
- ❌ **Missing ablations:** Don't just compare full system vs. naive
- ❌ **No error analysis:** What does your method fail on?
- ❌ **Overclaimed generalization:** "Only tested on 1 COBOL program" → "Works for all COBOL"
- ❌ **Reproducibility gaps:** No code, no data, vague hyperparameters
- ❌ **Insufficient baselines:** "Better than naive RAG" is weak; compare to industry standards
- ❌ **No human validation:** Automatic metrics miss subtleties

---

## 10. FINAL CHECKLIST

Before submission:

```
[ ] Ground truth annotations exist for all test queries
[ ] 3+ real COBOL programs included
[ ] Quantitative metrics: Precision, Recall, NDCG, F1
[ ] 5 baselines implemented and evaluated
[ ] Human evaluation completed (≥3 raters, Cohen's kappa > 0.7)
[ ] All code has type hints & docstrings
[ ] Unit tests pass (>80% coverage)
[ ] CI/CD pipeline green on all Python versions
[ ] Paper written & reviewed by 2+ peers
[ ] Related work table updated
[ ] Reproducibility statement (code, data, hyperparameters)
[ ] Public GitHub repo with clear README
[ ] Submitted to target venue with signed statement
```

---

## Next Immediate Action

**Pick ONE of these to start:**

1. **Evaluation Path** (Fastest): Add metrics + ground truth → Run ablation → Get results
2. **Dataset Path** (Longest lead): Find 3-5 real COBOL programs → Extract parser outputs
3. **Baseline Path** (Quickest win): Implement 5 baselines → Compare → Create table

**Recommendation: Start with Evaluation Path** (highest ROI in 2-3 weeks)
