# src/utils/response_utils.py
from datetime import datetime
from src.responses.agenda_response import AgendaResponse, TimeSlot

def map_entity_to_response(entity: dict) -> AgendaResponse:
    return AgendaResponse(
        id=entity['RowKey'],
        summary=entity['summary'],
        description=entity.get('description'),
        location=entity.get('location'),
        itemType=entity['itemType'],
        created=datetime.fromisoformat(entity['created']),
        updated=datetime.fromisoformat(entity['updated']),
        timeSlot=TimeSlot(
            start=datetime.fromisoformat(entity['timeSlotStart']),
            end=datetime.fromisoformat(entity['timeSlotEnd'])
        )
    )
