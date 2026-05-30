from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.order import Address
from app.schemas.user import AddressCreate, AddressUpdate, AddressResponse

router = APIRouter(prefix="/users/me/addresses", tags=["addresses"])


@router.get("", response_model=List[AddressResponse])
async def list_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Address).filter(Address.user_id == current_user.id).all()


@router.post("", response_model=AddressResponse, status_code=201)
async def create_address(
    data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id
        ).update({"is_default": False})
    addr = Address(**data.model_dump(), user_id=current_user.id)
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    data: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addr = db.query(Address).filter(
        Address.id == address_id, Address.user_id == current_user.id
    ).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    if data.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id
        ).update({"is_default": False})
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(addr, field, value)
    db.commit()
    db.refresh(addr)
    return addr


@router.delete("/{address_id}", status_code=204)
async def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addr = db.query(Address).filter(
        Address.id == address_id, Address.user_id == current_user.id
    ).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    count = db.query(Address).filter(Address.user_id == current_user.id).count()
    if count <= 1:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu única dirección guardada")
    db.delete(addr)
    db.commit()


@router.put("/{address_id}/default", response_model=AddressResponse)
async def set_default_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addr = db.query(Address).filter(
        Address.id == address_id, Address.user_id == current_user.id
    ).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    db.query(Address).filter(Address.user_id == current_user.id).update({"is_default": False})
    addr.is_default = True
    db.commit()
    db.refresh(addr)
    return addr
