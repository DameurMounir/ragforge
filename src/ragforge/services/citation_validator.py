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
    _EXCERPT = re.compile(
        r'(?P<claim>.+?)\s+\[Sources? (?P<numbers>[0-9]{1,6}(?:,\s*[0-9]{1,6})*)\]\.?'
    )
    _SENTENCE_BREAK = re.compile(r'(?<=[.!?؟。！])\s+')
    ABSTENTION = 'The cited evidence is insufficient. Source review is required.'

    def verify_excerpts(self, answer: str, passages: dict[int, str]) -> dict[str, Any]:
        """Keep only complete extractive sentences found in every cited passage."""
        sentences = {}
        for number, passage in passages.items():
            normalized = ' '.join(passage.split())
            sentences[number] = {
                sentence.removesuffix('.'): sentence
                for sentence in self._SENTENCE_BREAK.split(normalized)
                if sentence and not sentence.endswith(('...', '…'))
            }

        accepted = []
        rejected = 0
        invalid_numbers = set()
        for line in answer.splitlines():
            if not line.strip():
                continue
            match = self._EXCERPT.fullmatch(' '.join(line.split()))
            if match is None or self.SOURCE_PATTERN.search(match['claim']):
                rejected += 1
                continue
            numbers = [int(value) for value in match['numbers'].split(',')]
            invalid_numbers.update(set(numbers) - passages.keys())
            claim = match['claim'].removesuffix('.')
            if not all(claim in sentences.get(number, {}) for number in numbers):
                rejected += 1
                continue
            label = 'Source' if len(numbers) == 1 else 'Sources'
            citation = ', '.join(str(number) for number in numbers)
            accepted.append(f'{sentences[numbers[0]][claim]} [{label} {citation}]')

        return {
            'policy': 'verbatim',
            'answer': '\n'.join(accepted) if accepted else self.ABSTENTION,
            'accepted_claims': len(accepted),
            'rejected_claims': rejected,
            'invalid_source_numbers': sorted(invalid_numbers),
            'review_required': bool(rejected or not accepted),
        }

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
        missing_support = False

        if invalid_numbers:
            # A wholly invalid attribution must not turn into a free-standing claim.
            missing_support = any(
                not valid_set.intersection(int(n) for n in self.NUMBER_PATTERN.findall(group))
                for group in self.SOURCE_PATTERN.findall(answer)
            )
            if missing_support:
                sanitized_answer = self.ABSTENTION
            else:
                sanitized_answer = self._remove_invalid_source_numbers(
                    answer=answer, valid_set=valid_set
                )
            was_modified = sanitized_answer != answer

        return {
            'valid_source_numbers': sorted(valid_set),
            'cited_source_numbers': cited_numbers,
            'invalid_source_numbers': invalid_numbers,
            'was_modified': was_modified,
            'review_required': missing_support,
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
