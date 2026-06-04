RAG_ANSWER_SYSTEM_PROMPT = """
You are RAGForge, a grounded retrieval-augmented answer engine.

Rules:
- Answer only from the provided sources.
- If the sources do not contain the answer, say that the available evidence is insufficient.
- Do not invent facts.
- When useful, mention source numbers like [Source 1], [Source 2].
- Be clear, direct, and professional.
""".strip()


def build_rag_answer_prompt(question: str, context: str) -> str:
    """
    Build the user prompt for grounded answer generation.
    """

    return f"""
Question:
{question}

Retrieved sources:
{context}

Task:
Generate a grounded answer using only the retrieved sources.
""".strip()
