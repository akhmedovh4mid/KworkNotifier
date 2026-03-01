from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Want:
    id: int
    url: str
    name: str
    description: str
    date_view: str | None
    price_limit: float
    possible_price_limit: float

    @classmethod
    def from_dict(cls, want: dict[str, Any]) -> "Want":
        return cls(
            id=int(want["id"]),
            name=str(want["name"]),
            description=str(want["description"]),
            price_limit=float(want["priceLimit"]),
            possible_price_limit=float(want["possiblePriceLimit"]),
            url=f"https://kwork.ru/projects/{int(want['id'])}/view",
            date_view=want["dateView"],
        )
