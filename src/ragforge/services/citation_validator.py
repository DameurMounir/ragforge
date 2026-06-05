import re
from typing import Any


class CitationValidator:
    """
    Validate and optionally sanitize source citations in generated answers.

    The LLM is allowed to cite only source numbers that exist in the context
    constructed by RAGContextBuilder. This service prevents cases such as an
    answer citing [Source 13] when the response contains only 5 sources.
    """

    SOURCE_PATTERN = re.compile(r'\[(Sources?\s+[^\]]+)\]')
    NUMBER_PATTERN = re.compile(r'\d+')

    def validate_and_sanitize(
        self,
        answer: str,
        valid_source_numbers: list[int],
    ) -> dict[str, Any]:
        """
        Return a validation report and an answer with invalid source numbers
        removed from citation brackets.
        """
        valid_set = set(valid_source_numbers)
        cited_numbers = self.extract_cited_source_numbers(answer)
        invalid_numbers = sorted(number for number in cited_numbers if number not in valid_set)

        sanitized_answer = answer
        was_modified = False

        if invalid_numbers:
            sanitized_answer = self._remove_invalid_source_numbers(
                answer=answer,
                valid_set=valid_set,
            )
            was_modified = sanitized_answer != answer

        return {
            'valid_source_numbers': sorted(valid_set),
            'cited_source_numbers': cited_numbers,
            'invalid_source_numbers': invalid_numbers,
            'was_modified': was_modified,
            'answer': sanitized_answer,
        }

    def extract_cited_source_numbers(self, answer: str) -> list[int]:
        """
        Extract source numbers from citation brackets.
        """
        numbers: set[int] = set()

        for match in self.SOURCE_PATTERN.finditer(answer):
            citation_text = match.group(1)

            for number_text in self.NUMBER_PATTERN.findall(citation_text):
                numbers.add(int(number_text))

        return sorted(numbers)

    def _remove_invalid_source_numbers(
        self,
        answer: str,
        valid_set: set[int],
    ) -> str:
        def replace(match: re.Match) -> str:
            citation_text = match.group(1)
            citation_numbers = [
                int(number_text)
                for number_text in self.NUMBER_PATTERN.findall(citation_text)
            ]
            valid_numbers = [
                number
                for number in citation_numbers
                if number in valid_set
            ]

            if not valid_numbers:
                return ''

            label = 'Source' if len(valid_numbers) == 1 else 'Sources'
            joined_numbers = ', '.join(str(number) for number in valid_numbers)
            return f'[{label} {joined_numbers}]'

        sanitized = self.SOURCE_PATTERN.sub(replace, answer)
        sanitized = re.sub(r'\s{2,}', ' ', sanitized).strip()
        sanitized = re.sub(r'\s+([.,;:])', r'\1', sanitized)
        return sanitized
