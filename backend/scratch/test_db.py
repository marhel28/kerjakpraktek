import asyncio
from backend.db.main import db_session_maker
from backend.auth.service import UserService
from backend.auth.utility import create_access_token, build_user_payload
from backend.auth.model import UserRole

async def main():
    user_service = UserService()
    async with db_session_maker() as s:
        u = await user_service.get_user_by_email('ammarmaulahela20@gmail.com', s)
        if u:
            print(f"USER: {u.username}, ROLE: {repr(u.role)}, type: {type(u.role)}")
            print(f"UserRole.ADMIN: {repr(UserRole.ADMIN)}")
            print(f"Match with UserRole.ADMIN: {u.role == UserRole.ADMIN}")
            print(f"Match with 'admin': {str(u.role).lower() == 'admin'}")
            
            token = create_access_token(build_user_payload(u))
            print(f"ADMIN TOKEN: {token}")

if __name__ == "__main__":
    asyncio.run(main())
