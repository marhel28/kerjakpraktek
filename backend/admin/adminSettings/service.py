from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.data.settings.model import SystemSetting
from typing import List, Dict, Any

class AdminSettingService:
    
    @staticmethod
    async def get_setting(session: AsyncSession, key: str) -> Any:
        statement = select(SystemSetting).where(SystemSetting.key == key)
        result = await session.execute(statement)
        setting = result.scalar_one_or_none()
        return setting.value if setting else None

    @staticmethod
    async def update_setting(session: AsyncSession, key: str, value: Any, description: str = None):
        statement = select(SystemSetting).where(SystemSetting.key == key)
        result = await session.execute(statement)
        setting = result.scalar_one_or_none()
        
        if not setting:
            setting = SystemSetting(key=key, value=value, description=description)
            session.add(setting)
        else:
            setting.value = value
            if description:
                setting.description = description
            session.add(setting)
            
        await session.commit()
        await session.refresh(setting)
        return setting

    @staticmethod
    async def get_courier_preferences(session: AsyncSession) -> Dict[str, bool]:
        # Default couriers
        defaults = {
            "jne": True,
            "jnt": True,
            "sicepat": True,
            "tiki": False,
            "pos": False,
            "wahana": False,
            "anteraja": False
        }
        
        stored = await AdminSettingService.get_setting(session, "active_couriers")
        if stored:
            # Merge stored values with defaults (in case new couriers are added to system)
            for k, v in stored.items():
                if k in defaults:
                    defaults[k] = v
                    
        return defaults
