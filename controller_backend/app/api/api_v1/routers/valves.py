from fastapi import APIRouter, Request, Depends, Response, encoders
import typing as t

from app.db.session import get_db
from app.db.crud import (
    get_valves,
    get_valve,
    create_valve,
    delete_valve,
    edit_valve,
)
from app.db.schemas import ValveCreate, ValveEdit, Valve, ValveOut
from app.core.auth import get_current_active_user, get_current_active_superuser
from app.core.action_config import open_valve, close_valve, toggle_valve

valves_router = r = APIRouter()


# @r.get(
#     "/valves",
#     response_model=t.List[Valve],
#     response_model_exclude_none=True,
# )
# async def valves_list(
#     response: Response,
#     db=Depends(get_db)
# ):
#     """
#     Get all valves
#     """
#     valves = get_valves(db)
#     # This is necessary for react-admin to work
#     response.headers["Content-Range"] = f"0-9/{len(valves)}"
#     return valves


# @r.get(
#     "/valves/{valve_id}",
#     response_model=Valve,
#     response_model_exclude_none=True,
# )
# async def valve_details(
#     request: Request,
#     valve_id: str,
#     db=Depends(get_db)
# ):
#     """
#     Get any valve details
#     """
#     valve = get_valve(db, valve_id)
#     return valve
#     # return encoders.jsonable_encoder(
#     #     user, skip_defaults=True, exclude_none=True,
#     # )


# @r.post("/valves", response_model=Valve, response_model_exclude_none=True)
# async def valve_create(
#     request: Request,
#     valve: ValveCreate,
#     db=Depends(get_db)
# ):
#     """
#     Create a new valve
#     """
#     return create_valve(db, valve)


@r.put(
    "/valves/{action}/{valve_id}"
)
async def valve_action(
    request: Request,
    valve_id: str,
    action: str,
    current_user=Depends(get_current_active_superuser),
    db=Depends(get_db)
):
    """
    Update existing valve
    """
    if action.lower() == 'close':
        return close_valve(valve_id, None, db)
    elif action.lower() == 'open':
        return open_valve(valve_id, None, db)
    elif action.lower() == 'toggle':
        return toggle_valve(valve_id, None, db)
    else:
        return {'message': 'Unknown action {}'.format(action)}


# @r.put(
#     "/valves/{valve_id}", response_model=Valve, response_model_exclude_none=True
# )
# async def valve_edit(
#     request: Request,
#     valve_id: str,
#     valve: ValveEdit,
#     db=Depends(get_db)
# ):
#     """
#     Update existing valve
#     """
#     return edit_valve(db, valve_id, valve)


# @r.delete(
#     "/valves/{valve_id}", response_model=Valve, response_model_exclude_none=True
# )
# async def valve_delete(
#     request: Request,
#     valve_id: str,
#     db=Depends(get_db)
# ):
#     """
#     Delete existing valve
#     """
#     return delete_valve(db, valve_id)
