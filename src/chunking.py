"""Implement fixed-size and structure-aware chunking."""
import re
from .models import Chunk, DocumentPage


def fixed_size(page: DocumentPage, size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Split page text into overlapping windows of fixed character length.
    
    Retains page metadata, document_id, source, and page number.
    """
    text = page.text
    step = size - overlap
    if step <= 0:
        raise ValueError("chunk_size must be strictly greater than overlap")

    chunks: list[Chunk] = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = min(start + size, len(text))
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunk_id = f"{page.document_id}_p{page.page}_fix_{chunk_index:03d}"
            chunk_metadata = dict(page.metadata)
            chunk_metadata.update({
                "chunk_strategy": "fixed_size",
                "chunk_size": len(chunk_text),
                "start_char": start,
                "end_char": end
            })
            chunks.append(Chunk(
                chunk_id=chunk_id,
                document_id=page.document_id,
                source=page.source,
                page=page.page,
                text=chunk_text,
                metadata=chunk_metadata
            ))
            chunk_index += 1
        
        if end >= len(text):
            break
        start += step

    return chunks


def by_paragraph(page: DocumentPage, max_size: int = 800) -> list[Chunk]:
    """Structure-aware chunking: groups logical paragraphs, splits oversized units cleanly.
    
    Preserves heading and complete sentences to maximize semantic coherence.
    """
    raw_paras = [p.strip() for p in page.text.split("\n\n") if p.strip()]
    refined_units: list[str] = []

    # If any paragraph is oversized, split it by sentence boundaries
    for p in raw_paras:
        if len(p) <= max_size:
            refined_units.append(p)
        else:
            # Split by sentence endings (. , ? , ! , \n)
            sentences = re.split(r"(?<=[.?!;])\s+", p)
            current_unit = ""
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue
                if len(current_unit) + len(sent) + 1 <= max_size:
                    current_unit = f"{current_unit} {sent}".strip()
                else:
                    if current_unit:
                        refined_units.append(current_unit)
                    current_unit = sent
            if current_unit:
                refined_units.append(current_unit)

    # Now group refined units into chunks up to max_size
    chunks: list[Chunk] = []
    chunk_index = 0
    current_chunk_text = ""

    for unit in refined_units:
        if len(current_chunk_text) + len(unit) + 2 <= max_size:
            if current_chunk_text:
                current_chunk_text = f"{current_chunk_text}\n\n{unit}"
            else:
                current_chunk_text = unit
        else:
            if current_chunk_text:
                chunk_id = f"{page.document_id}_p{page.page}_para_{chunk_index:03d}"
                chunk_metadata = dict(page.metadata)
                chunk_metadata.update({
                    "chunk_strategy": "by_paragraph",
                    "chunk_size": len(current_chunk_text)
                })
                chunks.append(Chunk(
                    chunk_id=chunk_id,
                    document_id=page.document_id,
                    source=page.source,
                    page=page.page,
                    text=current_chunk_text,
                    metadata=chunk_metadata
                ))
                chunk_index += 1
            current_chunk_text = unit

    if current_chunk_text:
        chunk_id = f"{page.document_id}_p{page.page}_para_{chunk_index:03d}"
        chunk_metadata = dict(page.metadata)
        chunk_metadata.update({
            "chunk_strategy": "by_paragraph",
            "chunk_size": len(current_chunk_text)
        })
        chunks.append(Chunk(
            chunk_id=chunk_id,
            document_id=page.document_id,
            source=page.source,
            page=page.page,
            text=current_chunk_text,
            metadata=chunk_metadata
        ))

    return chunks
