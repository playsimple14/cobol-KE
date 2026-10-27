import re
from typing import List, Set
from ..models import CodeChunk
from ..ingestion.koopa_loader import KoopaLoader

class ASTChunker:
    """
    Syntax and AST-aware chunker for COBOL.
    Segments code at logical Paragraph boundaries rather than fixed token lengths,
    while mapping referenced variables and AST statements.
    """

    def __init__(self, loader: KoopaLoader):
        self.loader = loader

    def chunk_procedure_division(self) -> List[CodeChunk]:
        chunks: List[CodeChunk] = []
        ast = self.loader.ast_data

        # Locate procedureDivision in Koopa AST
        proc_div = None
        for child in ast.get("children", []):
            if child.get("node_type") == "procedureDivision":
                proc_div = child
                break

        if not proc_div:
            # Fallback to call graph nodes if AST format differs
            for node_id, node in self.loader.call_nodes.items():
                raw = self.loader.get_source_slice(node.start_line, node.end_line)
                ref_symbols = self._extract_symbols_from_text(raw)
                chunks.append(
                    CodeChunk(
                        chunk_id=node.id,
                        paragraph_name=node.id,
                        start_line=node.start_line,
                        end_line=node.end_line,
                        raw_code=raw,
                        ast_statements=[],
                        referenced_symbols=list(ref_symbols)
                    )
                )
            return chunks

        # Extract from procedureDivision paragraphs
        for para in proc_div.get("paragraphs", []):
            name = para["name"]
            start_l = para["start_line"]
            end_l = para["end_line"]
            raw_code = self.loader.get_source_slice(start_l, end_l)
            ast_stmts = para.get("statements", [])

            # Identify all referenced symbols in this chunk
            ref_symbols = self._extract_symbols_from_text(raw_code)

            chunks.append(
                CodeChunk(
                    chunk_id=name,
                    paragraph_name=name,
                    start_line=start_l,
                    end_line=end_l,
                    raw_code=raw_code,
                    ast_statements=ast_stmts,
                    referenced_symbols=list(ref_symbols)
                )
            )

        return chunks

    def _extract_symbols_from_text(self, text: str) -> Set[str]:
        """
        Scans code chunk for known symbols from the Symbol Table
        and 88-level condition names.
        """
        found = set()
        # Look for symbol table variables
        for sym_name in self.loader.symbol_table.keys():
            # Match word boundary
            pattern = r'\b' + re.escape(sym_name) + r'\b'
            if re.search(pattern, text):
                found.add(sym_name)

        # Look for 88 condition names and include their parent symbols too
        for cond_name, parent_sym in self.loader.condition_88_to_parent.items():
            pattern = r'\b' + re.escape(cond_name) + r'\b'
            if re.search(pattern, text):
                found.add(cond_name)
                found.add(parent_sym)

        return found
