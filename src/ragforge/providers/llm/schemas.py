from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


LLMRole = Literal['system', 'user', 'assistant']


class LLMMessage(BaseModel):
    """
    Provider-neutral message schema.
    """

    role: LLMRole
    content: str = Field(min_length=1)


class LLMGenerationRequest(BaseModel):
    """
    Provider-neutral generation request.

    The caller can use:
    - prompt + optional system_prompt
    - or a full messages list
    """

    provider: str | None = None
    model: str | None = None

    prompt: str | None = None
    system_prompt: str | None = None
    messages: list[LLMMessage] | None = None

    temperature: float | None = Field(default=None, ge=0, le=2)
    max_output_tokens: int | None = Field(default=None, gt=0)

    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_prompt_or_messages(self):
        if not self.prompt and not self.messages:
            raise ValueError('Either prompt or messages must be provided.')

        return self

    def to_messages(self) -> list[LLMMessage]:
        """
        Normalize prompt/system_prompt into a messages list.
        """

        if self.messages:
            return self.messages

        normalized_messages: list[LLMMessage] = []

        if self.system_prompt:
            normalized_messages.append(
                LLMMessage(role='system', content=self.system_prompt)
            )

        if self.prompt:
            normalized_messages.append(
                LLMMessage(role='user', content=self.prompt)
            )

        return normalized_messages


class LLMUsage(BaseModel):
    """
    Token usage returned by the provider when available.
    """

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


class LLMGenerationResponse(BaseModel):
    """
    Provider-neutral generation response.
    """

    signal: str = 'llm_generation_success'
    provider: str
    model: str
    content: str
    finish_reason: str | None = None
    usage: LLMUsage | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)