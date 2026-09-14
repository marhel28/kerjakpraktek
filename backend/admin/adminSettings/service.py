from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.data.settings.model import SystemSetting
from backend.db.redis import cache_get, cache_set, cache_delete
from typing import List, Dict, Any

SETTINGS_CACHE_PREFIX = "setting:"
SETTINGS_CACHE_TTL = 3600  # 1 jam


class AdminSettingService:
    
    @staticmethod
    async def get_setting(session: AsyncSession, key: str) -> Any:
        cache_key = f"{SETTINGS_CACHE_PREFIX}{key}"
        cached = await cache_get(cache_key)
        if cached is not None:
            return cached

        statement = select(SystemSetting).where(SystemSetting.key == key)
        result = await session.execute(statement)
        setting = result.scalar_one_or_none()
        val = setting.value if setting else None
        if val is not None:
            await cache_set(cache_key, val, ex=SETTINGS_CACHE_TTL)
        return val

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

        # Invalidate cache
        await cache_delete(f"{SETTINGS_CACHE_PREFIX}{key}")
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
