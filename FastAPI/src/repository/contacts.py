from fastapi import HTTPException, status
from sqlalchemy import Date, select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import and_

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    result = await db.execute(stmt)
    todos = result.scalars().all()
    return todos


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    return contact


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    # Перевірка наявності контакту в базі по імені, призвіщу
    existing_contact = await db.execute(
        select(Contact).filter_by(
            first_name=body.first_name, 
            last_name=body.last_name,
            email=body.email
            )
    )
    existing_contact = existing_contact.fetchone()
    if existing_contact:
        raise HTTPException(
            status_code=400,
            detail="Contact is already exist",
        )
    contact = Contact(**body.model_dump(), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def update_contact(
    contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User
):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact is None:
        return None
    for key, value in body.model_dump().items():
        setattr(contact, key, value)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contact_by_email(contact_email: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(email=contact_email, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact is not found",
        )
    return contact


async def get_contact_by_last_name(
    contact_last_name: str, db: AsyncSession, user: User
):
    stmt = select(Contact).filter_by(last_name=contact_last_name, user=user)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacts not found",
        )
    return contacts


async def get_contact_by_birthday(contact_birthday: Date, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(birthday=contact_birthday, user=user)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacts not found",
        )
    return contacts


async def get_birthdays(db: AsyncSession, user: User):
    from datetime import datetime, timedelta
    from sqlalchemy import select, and_
    current_date = datetime.now()
    end_date = current_date + timedelta(days=7)
    stmt = select(Contact).filter(
        and_(
            Contact.birthday.between(current_date.date(), end_date.date()),
            Contact.user_id
            == user.id,  # Фільтруємо за ідентифікатором поточного користувача
        )
    )

    result = await db.execute(stmt)
    contacts = result.scalars().all()

    return contacts
