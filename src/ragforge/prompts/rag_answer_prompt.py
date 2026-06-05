RAG_ANSWER_SYSTEM_PROMPT = """
You are RAGForge, a grounded retrieval-augmented answer engine.

Rules:
- Answer only from the retrieved sources provided in the prompt.
- If the sources do not contain the answer, say that the available evidence is insufficient.
- Do not invent facts, names, dates, budgets, credentials, hidden configuration, or source numbers.
- Cite only source numbers that appear in the source inventory.
- Never cite a source number outside the source inventory.
- When useful, cite like [Source 1] or [Sources 1, 2].
- Be clear, direct, and professional.
""".strip()


def build_rag_answer_prompt(
    question: str,
    context: str,
    available_source_numbers: list[int] | None = None,
) -> str:
    """
    Build the user prompt for grounded answer generation.
    """
    if available_source_numbers:
        source_inventory = ', '.join(
            f'Source {number}'
            for number in available_source_numbers
        )
    else:
        source_inventory = 'No sources available'

    return f"""
Question:
{question}

Source inventory:
{source_inventory}

Retrieved sources:
{context}

Task:
Generate a grounded answer using only the retrieved sources.
Only cite source numbers listed in the source inventory.
If the evidence is insufficient, say that the available evidence is insufficient.
""".strip()
