from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AgentConfig:
    id: str
    slug: str
    name: str
    label: str
    instructions: str

    description: str = ""
    color: str = "blue"
    markdown: bool = True

    def __post_init__(self) -> None:
        campos = {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "label": self.label,
            "instructions": self.instructions,
        }

        for campo, valor in campos.items():
            if not isinstance(valor, str):
                raise TypeError(
                    f"{campo} precisa ser uma string."
                )

            if not valor.strip():
                raise ValueError(
                    f"{campo} não pode ser vazio."
                )

        # Identificadores devem ser armazenados de forma canônica.
        object.__setattr__(self, "id", self.id.strip())
        object.__setattr__(self, "slug", self.slug.strip())