from fastapi import APIRouter, Request, Depends, Response, encoders
import typing as t


from app.core.auth import get_current_active_user, get_current_active_superuser
from app.core.action_config import pressure_check

pressures_router = r = APIRouter()


@r.get(
    "/pressures"
)
async def valve_action(
    request: Request,
    current_user=Depends(get_current_active_superuser),
    db=Depends(get_db)
):
    """
    Update existing valve
    """
    return pressure_check()
