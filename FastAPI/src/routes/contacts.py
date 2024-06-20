from fastapi import APIRouter, HTTPException, Depends, status, Query

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.database.db import get_db
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponseSchema
from src.services.auth import auth_serviсe

from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=list[ContactResponseSchema],
    description="No more than 2 requests per minute",
    dependencies=[Depends(RateLimiter(times=2, seconds=60))],
)
async def get_contacts(
    limit: int = Query(default=10, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_serviсe.get_current_user)
):
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponseSchema)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_serviсe.get_current_user),
):
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post(
    "/",
    response_model=ContactResponseSchema,
    status_code=status.HTTP_201_CREATED,
    description="No more than 2 contacts per one minute",
    dependencies=[Depends(RateLimiter(times=2, seconds=60))],
)
async def create_contact(
    body: ContactSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_serviсe.get_current_user),
):
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_serviсe.get_current_user),
):
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact is not found"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponseSchema)
async def update_contact(
    body: ContactUpdateSchema,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_serviсe.get_current_user),
):
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact is not found"
        )
    return contact


@router.get("/email/{contact_email}", response_model=ContactResponseSchema)
async def get_contact_by_email(
    contact_email: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_serviсe.get_current_user),
):
    contact = await repositories_contacts.get_contact_by_email(contact_email, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get("/last_name/{contact_last_name}", response_model=list[ContactResponseSchema])
async def get_contact_by_last_name(
    contact_last_name: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_serviсe.get_current_user),
):
    contacts = await repositories_contacts.get_contact_by_last_name(
        contact_last_name, db, user
    )
    return contacts


@router.get("/birthday/{contact_birthday}", response_model=list[ContactResponseSchema])
async def get_contact_by_birthday(
    contact_birthday: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_serviсe.get_current_user),
):
    contacts = await repositories_contacts.get_contact_by_birthday(
        contact_birthday, db, user
    )
    return contacts


@router.get("/birthdays/", response_model=list[ContactResponseSchema])
async def get_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_serviсe.get_current_user),
):
    contacts = await repositories_contacts.get_birthdays(db, user)
    return contacts
