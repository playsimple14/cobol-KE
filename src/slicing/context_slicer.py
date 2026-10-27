from typing import List, Dict, Set
from ..models import CodeChunk, SymbolEntry, AssembledContext
from ..ingestion.koopa_loader import KoopaLoader

class ContextSlicer:
    """
    Slices the Symbol Table and traverses the Call Graph to assemble
    the complete semantic context for a given CodeChunk.
    """

    def __init__(self, loader: KoopaLoader):
        self.loader = loader

    def assemble_context(self, chunk: CodeChunk, call_hops: int = 1) -> AssembledContext:
        """
        Builds a self-contained AssembledContext containing:
        1. The code chunk
        2. Pruned Symbol Table slice (only variables used in this chunk)
        3. Call Graph callers and callees
        """
        # 1. Prune Symbol Table
        st_slice = self._slice_symbol_table(chunk.referenced_symbols)

        # 2. Extract Call Graph Neighborhood
        callers, callees = self._get_call_neighborhood(chunk.paragraph_name, hops=call_hops)

        # 3. Format context string for LLM prompt
        formatted_prompt = self._format_prompt_context(chunk, st_slice, callers, callees)

        return AssembledContext(
            chunk=chunk,
            symbol_table_slice=st_slice,
            callers=callers,
            callees=callees,
            formatted_prompt_context=formatted_prompt
        )

    def _slice_symbol_table(self, referenced_symbols: List[str]) -> List[SymbolEntry]:
        sliced_symbols: Dict[str, SymbolEntry] = {}

        for sym_name in referenced_symbols:
            # Check if it's a direct symbol
            if sym_name in self.loader.symbol_table:
                sym = self.loader.symbol_table[sym_name]
                sliced_symbols[sym.name] = sym
            # Check if it's an 88-condition
            elif sym_name in self.loader.condition_88_to_parent:
                parent_name = self.loader.condition_88_to_parent[sym_name]
                if parent_name in self.loader.symbol_table:
                    sliced_symbols[parent_name] = self.loader.symbol_table[parent_name]

        return list(sliced_symbols.values())

    def _get_call_neighborhood(self, paragraph_name: str, hops: int = 1):
        callers = set()
        callees = set()

        for edge in self.loader.call_edges:
            if edge.target == paragraph_name:
                callers.add(edge.source)
            if edge.source == paragraph_name:
                callees.add(edge.target)

        return sorted(list(callers)), sorted(list(callees))

    def _format_prompt_context(
        self,
        chunk: CodeChunk,
        st_slice: List[SymbolEntry],
        callers: List[str],
        callees: List[str]
    ) -> str:
        lines = []
        lines.append(f"### [PARAGRAPH: {chunk.paragraph_name}] (Lines {chunk.start_line}-{chunk.end_line})")
        lines.append("```cobol")
        lines.append(chunk.raw_code.strip())
        lines.append("```\n")

        lines.append("### DATA DICTIONARY (Symbol Table Slice for this Paragraph):")
        if not st_slice:
            lines.append("No specific Working-Storage variables mapped.")
        else:
            for sym in st_slice:
                pic_info = f", PIC: {sym.pic}" if sym.pic else ""
                default_info = f", Default: {sym.default}" if sym.default else ""
                parent_info = f", Record: {sym.parent}" if sym.parent else ""
                lines.append(f"- **{sym.name}** (Level {sym.level}{pic_info}{parent_info}{default_info})")
                if sym.condition_88s:
                    for c88 in sym.condition_88s:
                        val = c88.get("value") or c88.get("range")
                        lines.append(f"    * 88 {c88['name']} => {val}")

        lines.append("\n### EXECUTION FLOW (Call Graph Neighborhood):")
        callers_str = ", ".join(callers) if callers else "None (Entry Point or Unreferenced)"
        callees_str = ", ".join(callees) if callees else "None (Leaf execution)"
        lines.append(f"- **Called By:** {callers_str}")
        lines.append(f"- **Performs / Calls:** {callees_str}")

        return "\n".join(lines)
