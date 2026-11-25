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

    def __post_init__(self):
        campos = {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "label": self.label,
            "instructions": self.instructions,
        }

        for campo, valor in campos.items():
            if not valor or not valor.strip():
                raise ValueError(f"{campo} não pode ser vazio.")