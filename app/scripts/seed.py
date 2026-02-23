from datetime import date
from sqlmodel import Session, select

from app.core.db.engine import engine
from app.core.security import create_password_hash
from app.domain.entities.user import User
from app.domain.enums.roles_enum import UserRole


def seed_users():
    with Session(engine) as session:
        users_to_create = [
            {
                "first_name": "Andre",
                "last_name": "Admin",
                "cpf": "07644277412",
                "email": "admin@email.com",
                "role": UserRole.ADMIN,
                "first_access": False,
                "date_of_birth": date(1990, 1, 1),
            },
            {
                "first_name": "Team",
                "last_name": "Leader",
                "cpf": "11111111111",
                "email": "leader@email.com",
                "role": UserRole.TEAM_LEADER,
                "first_access": True,
                "date_of_birth": date(1992, 1, 1),
            },
            {
                "first_name": "Agent",
                "last_name": "Support",
                "cpf": "22222222222",
                "email": "agent@email.com",
                "role": UserRole.AGENT,
                "first_access": True,
                "date_of_birth": date(1993, 1, 1),
            },
            {
                "first_name": "Customer",
                "last_name": "User",
                "cpf": "33333333333",
                "email": "customer@email.com",
                "role": UserRole.CUSTOMER,
                "first_access": True,
                "date_of_birth": date(1995, 1, 1),
            },
        ]

        for data in users_to_create:
            existing = session.exec(select(User).where(User.email == data["email"])).first()

            if existing:
                print(f"User {data['email']} already exists.")
                continue

            password_hash = create_password_hash(data["cpf"])

            user = User(
                first_name=data["first_name"],
                last_name=data["last_name"],
                cpf=data["cpf"],
                email=data["email"],
                date_of_birth=data["date_of_birth"],
                role=data["role"],
                is_active=True,
                first_access=data["first_access"],
                password_hash=password_hash,
            )

            session.add(user)

        session.commit()

    print("Seed completed successfully.")


if __name__ == "__main__":
    seed_users()
