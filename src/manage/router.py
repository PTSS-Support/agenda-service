from fastapi import APIRouter

router = APIRouter(prefix="/manage", include_in_schema=False)


@router.get("/health")
def health() -> bool:
    return True
