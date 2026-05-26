from enum import Enum


class LLMProvider(str, Enum):
    """
    Supported LLM providers for generation.

    FAKE:
        Deterministic provider used for tests, CI, and local validation.

    OPENAI_COMPATIBLE:
        Provider using an OpenAI-compatible chat completions API.
    """

    FAKE = 'fake'
    OPENAI_COMPATIBLE = 'openai_compatible'