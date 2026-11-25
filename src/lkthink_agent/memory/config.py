from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MemoryConfig:
    enabled: bool = True
    fail_open: bool = True

    max_items: int = 20
    max_content_length: int = 4000
    max_context_chars: int = 12000

    def __post_init__(self) -> None:
        if self.max_items < 1:
            raise ValueError("max_items precisa ser maior que zero.")

        if self.max_content_length < 1:
            raise ValueError(
                "max_content_length precisa ser maior que zero."
            )

        if self.max_context_chars < 1:
            raise ValueError(
                "max_context_chars precisa ser maior que zero."
            )
