#!/usr/bin/env python3

from app.db.session import get_db, get_rdb
from app.db.crud import create_user
from app.db.crud import create_valve
from app.db.schemas import UserCreate
from app.db.schemas import ValveCreate
from app.db.session import SessionLocal


def init() -> None:
    db = SessionLocal()

    create_user(
        db,
        UserCreate(
            email="support@bramkas.com",
            password="password",
            is_active=True,
            is_superuser=True,
        ),
    )

    # create_valve(
    #     db,
    #     ValveCreate(
    #         name="V1",
    #         is_active=True,
    #         is_up=True,
    #         last_changed="By Balaji",
    #         state="open"
    #     ),
    # )

if __name__ == "__main__":
    print("Creating superuser support@bramkas.com")
    init()
    print("Superuser created")
