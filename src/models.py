"""
Data Models for COBOL Knowledge Extraction and Code RAG.
Uses standard Python dataclasses for zero-dependency execution.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class Condition88:
    name: str
    value: Optional[str] = None
    range: Optional[str] = None

@dataclass
class SymbolEntry:
    name: str
    level: str
    pic: Optional[str] = None
    section: str = "WORKING-STORAGE"
    parent: Optional[str] = None
    default: Optional[str] = None
    condition_88s: List[Dict[str, str]] = field(default_factory=list)
    redefines: Optional[str] = None

@dataclass
class CallGraphNode:
    id: str
    type: str
    start_line: int
    end_line: int

@dataclass
class CallGraphEdge:
    source: str
    target: str
    type: str  # PERFORM, GOTO, CALL
    line: int

@dataclass
class CodeChunk:
    chunk_id: str
    paragraph_name: str
    start_line: int
    end_line: int
    raw_code: str
    ast_statements: List[Dict[str, Any]] = field(default_factory=list)
    referenced_symbols: List[str] = field(default_factory=list)

@dataclass
class AssembledContext:
    chunk: CodeChunk
    symbol_table_slice: List[SymbolEntry]
    callers: List[str]
    callees: List[str]
    formatted_prompt_context: str = ""
