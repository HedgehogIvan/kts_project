from sqlalchemy import select, ChunkedIteratorResult, insert, delete, update

from ...admin.models import Admin, AdminModel
from ...base.base_accessor import BaseAccessor


class AdminAccessor(BaseAccessor):
    async def create_admin(self, login: str, password: str) -> Admin:
        query = insert(AdminModel).values(login=login, password=password)

        async with self.app.database.session() as session:
            res = await session.execute(query)
            # Достаем планируемый id для админа в базе
            id_ = res.inserted_primary_key[0]

            await session.commit()

        return Admin(id_, login, password)

    async def get_by_login(self, login: str) -> Admin | None:
        query = select(AdminModel).where(AdminModel.login == login)

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        admin: AdminModel = res.scalars().first()

        if admin:
            return Admin(admin.id, admin.login, admin.password)
        else:
            return None

    async def delete_admin(self, login: str):
        query = delete(AdminModel).where(AdminModel.login == login)

        async with self.app.database.session() as session:
            await session.execute(query)

            await session.commit()

    async def update_pass_admin(self, admin_login: str, new_pass: str):
        query = (
            update(AdminModel)
            .where(AdminModel.login == admin_login)
            .values(password=new_pass)
        )

        async with self.app.database.session() as session:
            await session.execute(query)

            await session.commit()
