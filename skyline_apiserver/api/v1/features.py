"""Read-only deployment configuration for console panel visibility."""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, StrictBool, StrictStr

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.config import CONF

router = APIRouter()


class KagentChat(BaseModel):
    """AI Assistant (kagent) settings from skyline.yaml `kagent_chat`."""

    url: StrictStr
    namespace: Optional[StrictStr] = None
    agent: Optional[StrictStr] = None
    ui_version: Optional[StrictStr] = None
    allowed_roles: List[StrictStr] = []


class Features(BaseModel):
    features: Dict[str, Optional[StrictBool]]
    # Sent only to signed-in users, like the flags themselves.
    kagent_chat: Optional[KagentChat] = None


@router.get("/features", response_model=Features)
async def list_features(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> Features:
    values = CONF.config.get("features")
    kagent_chat = CONF.config.get("kagent_chat")
    return Features(
        features={} if values is None else values,
        kagent_chat=None if kagent_chat is None else KagentChat(**kagent_chat),
    )
