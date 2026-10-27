import json
from typing import Dict, Any, Optional
from ..models import AssembledContext

BUSINESS_RULE_SYSTEM_PROMPT = """You are an expert Mainframe Modernization and COBOL Reverse Engineering Architect.
Your task is to analyze COBOL source paragraphs alongside their Symbol Table slice (Data Dictionary) and Call Graph to extract exact, unambiguous business rules.

For each rule, output structured markdown containing:
1. **Rule Identifier & Name**
2. **Trigger / Invocation Context** (Who calls this logic?)
3. **Preconditions / Decision Logic** (Exact 88-level condition codes or variable thresholds)
4. **Action / Computation Formula** (Formulas translated into mathematical/business terms)
5. **Data Dictionary Mapping** (Inputs used, outputs modified, and their data types/lengths)
6. **Decision Table (DMN format)** if multiple branches exist.

CRITICAL INSTRUCTIONS:
- Ground every single field name in the provided Symbol Table slice. Do NOT invent modern variable names.
- Interpret 88-level conditions accurately according to the ranges/values given.
"""

class RuleExtractor:
    """
    Extracts structured Business Rules from an AssembledContext.
    Supports offline deterministic rule formatting and live LLM integration.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model

    def build_prompt(self, context: AssembledContext, user_query: str) -> str:
        prompt = f"""{BUSINESS_RULE_SYSTEM_PROMPT}

=======================================================
CONTEXT FOR ANALYSIS
=======================================================
{context.formatted_prompt_context}

=======================================================
USER QUERY / EXTRACTION GOAL
=======================================================
Query: "{user_query}"

Extract the formal business rules, decision logic, and data lineage for this paragraph:
"""
        return prompt

    def extract_rules_offline(self, context: AssembledContext, user_query: str) -> Dict[str, Any]:
        """
        Deterministic rule synthesis for offline demonstration and CI testing
        when an LLM API key is not provided.
        """
        chunk = context.chunk
        p_name = chunk.paragraph_name
        st = context.symbol_table_slice

        inputs = [s.name for s in st if not s.name.startswith("WS-FINAL") and not s.name.startswith("WS-TOTAL")]
        outputs = [s.name for s in st if s.name.startswith("WS-FINAL") or s.name.startswith("WS-TOTAL") or "STATUS" in s.name]

        return {
            "paragraph": p_name,
            "lines": f"{chunk.start_line}-{chunk.end_line}",
            "caller_context": context.callers,
            "callees": context.callees,
            "referenced_symbols_count": len(st),
            "inputs": inputs,
            "outputs": outputs,
            "ast_statements_count": len(chunk.ast_statements),
            "prompt_preview": self.build_prompt(context, user_query)[:500] + "..."
        }
