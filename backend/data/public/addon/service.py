from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from uuid import UUID, uuid4
from .model import AddonGroup, AddonItem, CategoryAddonMapping, ProductAddonOverride
from backend.data.public.category.model import Category
import json

class AddonService:
    @staticmethod
    async def get_bundle_by_product(db: AsyncSession, product_id_or_slug: str, category_slug: Optional[str] = None, redis_client=None):
        # 1. Resolve product and its scope
        from backend.data.stock.model import Stock
        from backend.data.public.category.model import SubCategory, Category
        from sqlalchemy.orm import joinedload
        
        # Resolve identifier
        try:
            val_uuid = UUID(str(product_id_or_slug))
            stmt = select(Stock).where(or_(Stock.uuid == val_uuid, Stock.slug == str(product_id_or_slug)))
        except:
            stmt = select(Stock).where(Stock.slug == str(product_id_or_slug))

        res = await db.execute(stmt)
        prod = res.scalar_one_or_none()
        
        if not prod:
            return []
            
        product_uuid = prod.uuid
        addon_scope = prod.addon_scope # inherit | custom
        
        cache_key = f"product:addons:v2:{product_uuid}"
        
        if redis_client:
            try:
                cached = await redis_client.get(cache_key)
                if cached: return json.loads(cached)
            except: pass

        resolved_groups = []

        # 🚀 PRIORITY 1: STOCK CUSTOM ADDONS
        if addon_scope == "custom":
            # Fetch specifically mapped groups for this product
            from .model import StockAddonMapping
            ov_stmt = select(AddonGroup).join(StockAddonMapping).where(
                StockAddonMapping.stock_uuid == product_uuid,
                StockAddonMapping.is_active == True,
                AddonGroup.is_active == True
            ).options(joinedload(AddonGroup.items)).order_by(StockAddonMapping.sort_order)
            
            res = await db.execute(ov_stmt)
            resolved_groups = res.unique().scalars().all()

        # 🚀 PRIORITY 2: SUBCATEGORY ADDONS (If P1 empty)
        if not resolved_groups and prod.subcategory_slug:
            sub_stmt = select(SubCategory.uuid).join(Category).where(
                SubCategory.slug == prod.subcategory_slug,
                Category.slug == prod.category_slug
            )
            s_uuid = (await db.execute(sub_stmt)).scalars().first()
            
            if s_uuid:
                sub_add_stmt = select(AddonGroup).join(CategoryAddonMapping).where(
                    CategoryAddonMapping.subcategory_uuid == s_uuid,
                    CategoryAddonMapping.is_active == True,
                    AddonGroup.is_active == True
                ).options(joinedload(AddonGroup.items)).order_by(CategoryAddonMapping.sort_order)
                
                res = await db.execute(sub_add_stmt)
                resolved_groups = res.unique().scalars().all()

        # 🚀 PRIORITY 3: CATEGORY ADDONS (If P1 & P2 empty)
        if not resolved_groups and prod.category_slug:
            cat_stmt = select(Category.uuid).where(Category.slug == prod.category_slug)
            c_uuid = (await db.execute(cat_stmt)).scalars().first()
            
            if c_uuid:
                cat_add_stmt = select(AddonGroup).join(CategoryAddonMapping).where(
                    CategoryAddonMapping.category_uuid == c_uuid,
                    CategoryAddonMapping.is_active == True,
                    AddonGroup.is_active == True
                ).options(joinedload(AddonGroup.items)).order_by(CategoryAddonMapping.sort_order)
                
                res = await db.execute(cat_add_stmt)
                resolved_groups = res.unique().scalars().all()

        # 🚀 PRIORITY 4: GLOBAL ADDONS (If all above empty)
        if not resolved_groups:
            global_stmt = select(AddonGroup).where(
                AddonGroup.is_global == True,
                AddonGroup.is_active == True
            ).options(joinedload(AddonGroup.items)).order_by(AddonGroup.sort_order)
            
            res = await db.execute(global_stmt)
            resolved_groups = res.unique().scalars().all()

        # Format Response
        final_data = []
        for g in resolved_groups:
            final_data.append({
                "uuid": str(g.uuid),
                "name": g.name,
                "selection_type": g.selection_type,
                "is_required": g.is_required,
                "group_type": g.group_type, # required, optional, recommended
                "items": [
                    {
                        "uuid": str(i.uuid),
                        "name": i.name,
                        "description": i.description,
                        "price": float(i.price),
                        "weight": float(i.weight),
                        "image_url": i.image_url,
                        "stock": i.stock,
                        "allow_quantity": i.allow_quantity,
                        "max_quantity": i.max_quantity,
                        "is_active": i.is_active
                    } for i in g.items if i.is_active
                ]
            })

        if redis_client:
            await redis_client.set(cache_key, json.dumps(final_data), ex=3600)
            
        return final_data

    @staticmethod
    async def get_all_groups(db: AsyncSession):
        stmt = select(AddonGroup).order_by(AddonGroup.sort_order)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_group_items(db: AsyncSession, group_uuid: UUID):
        stmt = select(AddonItem).where(AddonItem.group_uuid == group_uuid)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create_group(db: AsyncSession, data: dict, redis_client=None):
        category_uuids = data.pop("category_uuids", [])
        
        # Filter out immutable fields
        fields_to_ignore = {"uuid", "created_at", "items"}
        filtered_data = {k: v for k, v in data.items() if k not in fields_to_ignore}
        
        group = AddonGroup(**filtered_data)
        db.add(group)
        await db.flush() # Get UUID
        
        # Create mappings
        from backend.data.public.category.model import Category, SubCategory
        for target_uuid in category_uuids:
            # Check if it's a subcategory
            sub_stmt = select(SubCategory.uuid).where(SubCategory.uuid == target_uuid)
            sub_res = await db.execute(sub_stmt)
            is_sub = sub_res.scalar_one_or_none()
            
            if is_sub:
                mapping = CategoryAddonMapping(
                    subcategory_uuid=target_uuid,
                    addon_group_uuid=group.uuid,
                    is_active=True
                )
            else:
                mapping = CategoryAddonMapping(
                    category_uuid=target_uuid,
                    addon_group_uuid=group.uuid,
                    is_active=True
                )
            db.add(mapping)
            
        await db.commit()
        await db.refresh(group)
        
        # Invalidate cache
        if redis_client:
            try:
                keys = await redis_client.keys("product:addons:*")
                if keys: await redis_client.delete(*keys)
            except: pass
            
        return group

    @staticmethod
    async def update_group(db: AsyncSession, group_uuid: UUID, data: dict, redis_client=None):
        category_uuids = data.pop("category_uuids", None)
        
        # 🔥 FIX: Filter out immutable fields and non-model fields
        # This prevents DataError when frontend sends string dates
        fields_to_ignore = {"uuid", "created_at", "items"}
        update_data = {k: v for k, v in data.items() if k not in fields_to_ignore}
        
        stmt = select(AddonGroup).where(AddonGroup.uuid == group_uuid)
        result = await db.execute(stmt)
        group = result.scalar_one_or_none()
        
        if group:
            for key, value in update_data.items():
                if hasattr(group, key):
                    setattr(group, key, value)
            
            if category_uuids is not None:
                # Remove old mappings
                from sqlalchemy import delete
                await db.execute(delete(CategoryAddonMapping).where(CategoryAddonMapping.addon_group_uuid == group_uuid))
                
                # Add new mappings (can be category or subcategory UUIDs)
                # For simplicity, we check if the UUID belongs to a Category or SubCategory
                from backend.data.public.category.model import Category, SubCategory
                for target_uuid in category_uuids:
                    # Check if it's a subcategory first
                    sub_stmt = select(SubCategory.uuid).where(SubCategory.uuid == target_uuid)
                    sub_res = await db.execute(sub_stmt)
                    is_sub = sub_res.scalar_one_or_none()
                    
                    if is_sub:
                        mapping = CategoryAddonMapping(
                            subcategory_uuid=target_uuid,
                            addon_group_uuid=group.uuid,
                            is_active=True
                        )
                    else:
                        mapping = CategoryAddonMapping(
                            category_uuid=target_uuid,
                            addon_group_uuid=group.uuid,
                            is_active=True
                        )
                    db.add(mapping)
                    
            await db.commit()
            await db.refresh(group)
            
            # Invalidate cache
            if redis_client:
                try:
                    keys = await redis_client.keys("product:addons:*")
                    if keys: await redis_client.delete(*keys)
                except: pass
        return group

    @staticmethod
    async def delete_group(db: AsyncSession, group_uuid: UUID, redis_client=None):
        stmt = select(AddonGroup).where(AddonGroup.uuid == group_uuid)
        result = await db.execute(stmt)
        group = result.scalar_one_or_none()
        if group:
            await db.delete(group)
            await db.commit()
            
            # Invalidate cache
            if redis_client:
                try:
                    keys = await redis_client.keys("product:addons:*")
                    if keys: await redis_client.delete(*keys)
                except: pass
                
            return True
        return False

    @staticmethod
    async def create_item(db: AsyncSession, data: dict):
        item = AddonItem(**data)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def update_item(db: AsyncSession, item_uuid: UUID, data: dict):
        stmt = select(AddonItem).where(AddonItem.uuid == item_uuid)
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()
        if item:
            for key, value in data.items():
                setattr(item, key, value)
            await db.commit()
            await db.refresh(item)
        return item

    @staticmethod
    async def delete_item(db: AsyncSession, item_uuid: UUID):
        stmt = select(AddonItem).where(AddonItem.uuid == item_uuid)
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()
        if item:
            await db.delete(item)
            await db.commit()
            return True
        return False

    @staticmethod
    async def get_stock_mappings(db: AsyncSession, stock_uuid: UUID) -> List[UUID]:
        from .model import StockAddonMapping
        stmt = select(StockAddonMapping.addon_group_uuid).where(StockAddonMapping.stock_uuid == stock_uuid)
        result = await db.execute(stmt)
        return [row for row in result.scalars().all()]

    @staticmethod
    async def sync_stock_mappings(db: AsyncSession, stock_uuid: UUID, group_uuids: List[UUID], redis_client=None):
        from .model import StockAddonMapping
        from sqlalchemy import delete
        
        # 1. Delete existing
        await db.execute(delete(StockAddonMapping).where(StockAddonMapping.stock_uuid == stock_uuid))
        
        # 2. Add new
        for i, group_uuid in enumerate(group_uuids):
            mapping = StockAddonMapping(
                uuid=uuid4(),
                stock_uuid=stock_uuid,
                addon_group_uuid=group_uuid,
                sort_order=i
            )
            db.add(mapping)
        
        await db.commit()
        
        # 3. Clear cache
        if redis_client:
            cache_key = f"product:addons:v2:{stock_uuid}"
            try:
                await redis_client.delete(cache_key)
            except: pass
        
        return True
