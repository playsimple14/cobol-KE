import json
from typing import Dict, List, Tuple
from ..models import SymbolEntry, CallGraphNode, CallGraphEdge

class KoopaLoader:
    """
    Ingests artifacts extracted from the Koopa COBOL Parser:
    - Raw COBOL Source
    - Symbol Table (ST)
    - Call Graph (CG)
    - AST Hierarchy
    """

    def __init__(self, source_path: str, st_path: str, cg_path: str, ast_path: str):
        self.source_path = source_path
        self.st_path = st_path
        self.cg_path = cg_path
        self.ast_path = ast_path

        self.source_lines: List[str] = []
        self.symbol_table: Dict[str, SymbolEntry] = {}
        # Also index 88-level condition names pointing to their parent symbol
        self.condition_88_to_parent: Dict[str, str] = {}
        self.call_nodes: Dict[str, CallGraphNode] = {}
        self.call_edges: List[CallGraphEdge] = []
        self.ast_data: Dict = {}

    def load_all(self):
        self._load_source()
        self._load_symbol_table()
        self._load_call_graph()
        self._load_ast()

    def _load_source(self):
        with open(self.source_path, "r", encoding="utf-8") as f:
            self.source_lines = f.readlines()

    def _load_symbol_table(self):
        with open(self.st_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data.get("symbols", []):
                sym = SymbolEntry(
                    name=item["name"],
                    level=item.get("level", "05"),
                    pic=item.get("pic"),
                    section=item.get("section", "WORKING-STORAGE"),
                    parent=item.get("parent"),
                    default=item.get("default"),
                    condition_88s=item.get("condition_88s", []),
                    redefines=item.get("redefines")
                )
                self.symbol_table[sym.name] = sym
                for c88 in sym.condition_88s:
                    self.condition_88_to_parent[c88["name"]] = sym.name

    def _load_call_graph(self):
        with open(self.cg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for node in data.get("nodes", []):
                cg_node = CallGraphNode(
                    id=node["id"],
                    type=node["type"],
                    start_line=node["start_line"],
                    end_line=node["end_line"]
                )
                self.call_nodes[cg_node.id] = cg_node
            for edge in data.get("edges", []):
                cg_edge = CallGraphEdge(
                    source=edge["source"],
                    target=edge["target"],
                    type=edge["type"],
                    line=edge["line"]
                )
                self.call_edges.append(cg_edge)

    def _load_ast(self):
        with open(self.ast_path, "r", encoding="utf-8") as f:
            self.ast_data = json.load(f)

    def get_source_slice(self, start_line: int, end_line: int) -> str:
        # COBOL lines are 1-indexed
        lines = self.source_lines[start_line - 1 : end_line]
        return "".join(lines)
