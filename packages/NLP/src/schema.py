from dataclasses import asdict, dataclass, field
from typing import List, Optional


@dataclass
class QueryRequirements:
	"""Representa la versión estructurada de una consulta en lenguaje natural.

	Esta clase está pensada para la PoC del caso de uso
	"ingeniero de mantenimiento". Más adelante se pueden añadir
	campos adicionales según el modelo de perfil de candidato.
	"""

	role: Optional[str] = None
	skills: List[str] = field(default_factory=list)
	location: Optional[str] = None
	years_experience: Optional[int] = None
	num_candidates: Optional[int] = None
	languages: List[str] = field(default_factory=list)


def query_requirements_to_dict(obj: QueryRequirements) -> dict:
	"""Convierte un ``QueryRequirements`` en un ``dict`` serializable.

	Pensado para exponer el resultado de ``parse_query`` en la API 
	sin acoplar este módulo al framework web.
	"""

	return asdict(obj)


__all__ = ["QueryRequirements", "query_requirements_to_dict"]

