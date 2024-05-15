from fastapi import APIRouter


router = APIRouter()


@router.post("/transactions")
async def create_transaction():
    pass


@router.get("/transactions/{transaction_id}")
async def get_transaction():
    pass


@router.get("/transactions")
async def get_transactions():
    pass


@router.post("/transactions/{transaction_id}/approve")
async def approve_transaction():
    pass


@router.post("/transactions/{transaction_id}/reject")
async def reject_transaction():
    pass


@router.post("/transactions/{transaction_id}/withdraw")
async def withdraw():
    pass