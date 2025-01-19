from fastapi import APIRouter, Request, HTTPException, Depends
from src.auth.decorators import authentication, Role
from src.auth.context import get_user_context
from src.dependancies import get_agenda_facade
from src.exceptions.error_codes import ErrorCode
from src.facades.agenda_facade import AgendaFacade
from src.requests.create_agenda_item_request import CreateAgendaItemRequest
from src.requests.get_agenda_items_request import AgendaQueryParams
from src.requests.update_agenda_item_request import UpdateAgendaItemRequest
from src.responses.agenda_response import AgendaResponse, TimeSlot
from src.utils.validate_date_params import validate_date_params
from src.utils.validation_util import validate_group_id

agenda_router = APIRouter(tags=["agenda-service"])


@agenda_router.get("/agenda/items")
@authentication([Role.PATIENT, Role.FAMILY_MEMBER, Role.PRIMARY_CAREGIVER])
async def list_agenda_items(
        request: Request,
        params: AgendaQueryParams = Depends(),
        facade: AgendaFacade = Depends(get_agenda_facade)
):
    print(f"Received start_date: {params.start_date}")
    print(f"Received end_date: {params.end_date}")

    user_context = get_user_context()
    validate_group_id(user_context)
    validate_date_params(params.start_date, params.end_date)
    return await facade.list_agenda_items(user_context.group_id, params.start_date, params.end_date)

@agenda_router.get("/agenda/items/{itemId}")
@authentication([Role.PATIENT, Role.FAMILY_MEMBER, Role.PRIMARY_CAREGIVER])
async def get_agenda_item(
    request: Request,
    itemId: str,
    facade: AgendaFacade = Depends(get_agenda_facade)
):
    user_context = get_user_context()
    validate_group_id(user_context)
    agenda_item = await facade.get_agenda_item(user_context.group_id, itemId)
    if not agenda_item:
        raise HTTPException(status_code=404, detail="Agenda item not found")
    return agenda_item

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

@agenda_router.put(
    "/agenda/items/{itemId}",
    response_model=AgendaResponse,
    description="Update an existing agenda item",
    responses={
        400: {"description": "Invalid request body or missing group ID"},
        401: {"description": "Invalid or missing authentication token"},
        403: {"description": "Insufficient permissions to access this resource"},
        404: {"description": "Agenda item not found"}
    }
)
@authentication([Role.PATIENT, Role.FAMILY_MEMBER, Role.PRIMARY_CAREGIVER])
async def update_agenda_item(
    request: Request,
    itemId: str,
    item: UpdateAgendaItemRequest,
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

    updated_item = await facade.update_agenda_item(
        group_id=str(user_context.group_id),
        item_id=itemId,
        summary=item.summary,
        description=item.description,
        location=item.location,
        item_type=item.itemType,
        time_slot=time_slot
    )

    if not updated_item:
        raise HTTPException(status_code=404, detail="Agenda item not found")

    return updated_item

@agenda_router.delete(
    "/agenda/items/{itemId}",
    status_code=204,
    description="Delete an agenda item by its ID",
    responses={
        204: {"description": "Agenda item deleted successfully"},
        404: {"description": "Agenda item not found"},
        401: {"description": "Invalid or missing authentication token"},
        403: {"description": "Insufficient permissions to access this resource"}
    }
)
@authentication([Role.PATIENT, Role.FAMILY_MEMBER, Role.PRIMARY_CAREGIVER])
async def delete_agenda_item(
        request: Request,
        itemId: str,
        facade: AgendaFacade = Depends(get_agenda_facade)
):
    user_context = get_user_context()
    if not user_context or not user_context.group_id:
        raise HTTPException(status_code=400, detail="Group ID is required")

    deleted = await facade.delete_agenda_item(user_context.group_id, itemId)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agenda item not found")
