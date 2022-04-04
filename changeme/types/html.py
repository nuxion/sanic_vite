from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class HtmlData(BaseModel):
    # navbar: List[MenuOption]
    ctx: Dict[str, Any]
    title: str
    content: Dict[str, Any]
    meta: Optional[Dict[str, str]] = None
