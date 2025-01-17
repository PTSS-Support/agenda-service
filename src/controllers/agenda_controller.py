from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
from src.auth.decorators import authentication, Role
from src.auth.context import get_user_context
from src.dependancies import get_agenda_facade
from src.facades.agenda_facade import AgendaFacade
from src.requests.get_agenda_items_request import AgendaQueryParams
from src.responses.agenda_response import AgendaResponse

agenda_router = APIRouter(tags=["agenda-service"])


@agenda_router.get(
    "/agenda/items",
    response_model=List[AgendaResponse],
    description="List all agenda items",
    responses={
        401: {"description": "Invalid or missing authentication token"},
        403: {"description": "Insufficient permissions to access this resource"}
    }
)
@authentication([Role.CORE_USER, Role.FAMILY_MEMBER])
async def list_agenda_items(
        request: Request,
        params: AgendaQueryParams = Depends(),
        facade: AgendaFacade = Depends(get_agenda_facade)
) -> List[AgendaResponse]:
    user_context = get_user_context()
    if not user_context or not user_context.group_id:
        raise HTTPException(status_code=400, detail="Group ID is required")

    return await facade.list_agenda_items(user_context.group_id, AgendaQueryParams.start_date, AgendaQueryParams.end_date)