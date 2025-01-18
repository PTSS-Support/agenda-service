from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
from src.auth.decorators import authentication, Role
from src.auth.context import get_user_context
from src.dependancies import get_agenda_facade
from src.exceptions.error_codes import ErrorCode
from src.facades.agenda_facade import AgendaFacade
from src.requests.create_agenda_item_request import CreateAgendaItemRequest
from src.requests.get_agenda_items_request import AgendaQueryParams
from src.responses.agenda_response import AgendaResponse, TimeSlot

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
@authentication([Role.PATIENT, Role.FAMILY_MEMBER, Role.PRIMARY_CAREGIVER])
async def list_agenda_items(
        request: Request,
        params: AgendaQueryParams = Depends(),
        facade: AgendaFacade = Depends(get_agenda_facade)
) -> List[AgendaResponse]:
    user_context = get_user_context()
    if not user_context or not user_context.group_id:
        raise HTTPException(status_code=400, detail="Group ID is required")

    return await facade.list_agenda_items(user_context.group_id, params.start_date, params.end_date)

@agenda_router.post(
    "/agenda/items",
    response_model=AgendaResponse,
    description="Create a new agenda item",
    responses={
        400: {"description": "Invalid request body or missing group ID"},
        401: {"description": "Invalid or missing authentication token"},
        403: {"description": "Insufficient permissions to access this resource"}
    }
)
@authentication([Role.PATIENT, Role.FAMILY_MEMBER, Role.PRIMARY_CAREGIVER])
async def create_agenda_item(
    request: Request,
    item: CreateAgendaItemRequest,
    facade: AgendaFacade = Depends(get_agenda_facade)
) -> AgendaResponse:
    user_context = get_user_context()
    if not user_context or not user_context.group_id:
        raise HTTPException(
            status_code=ErrorCode.INVALID_GROUP_ID.status,
            detail={
                "code": ErrorCode.INVALID_GROUP_ID.code,
                "message": "Group ID is required"
            }
        )

    time_slot = TimeSlot(
        start=item.timeSlot.startTime,
        end=item.timeSlot.endTime
    )

    return await facade.create_agenda_item(
        group_id=str(user_context.group_id),
        summary=item.summary,
        description=item.description,
        location=item.location,
        item_type=item.itemType,
        time_slot=time_slot
    )