"""
Test suite mandiri untuk memverifikasi logika trigger notifikasi
pembayaran, pengiriman, dan booking service (User & Admin).
"""
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

async def test_admin_notification_helper():
    from backend.data.transaksi.service import _send_notification_to_admins
    from backend.auth.model import User, UserRole, UserMap

    session = AsyncMock()
    
    # Mock admin user query
    admin_user = User(
        uuid=uuid4(),
        username="admin_test",
        email="admin@example.com",
        password_hash="hash",
        role=UserRole.ADMIN
    )
    user_map = UserMap(
        local_user_id=str(admin_user.uuid),
        supabase_user_id="sub-admin-123"
    )

    # Setup session.execute return values for admin query & user_map query
    res_admin = MagicMock()
    res_admin.scalars.return_value.all.return_value = [admin_user]
    
    res_map = MagicMock()
    res_map.scalars.return_value.all.return_value = [user_map]
    
    session.execute.side_effect = [res_admin, res_map]

    with patch("backend.db.supabse.SupabaseNotificationService.bulk_notification", new_callable=AsyncMock) as mock_bulk:
        await _send_notification_to_admins(
            session=session,
            title="Test Admin Title",
            content="Test Content",
            action_url="/test",
            notif_type="order"
        )
        assert mock_bulk.called, "bulk_notification should be called for admins"
        call_args = mock_bulk.call_args.kwargs
        assert call_args["user_ids"] == ["sub-admin-123"]
        assert call_args["title"] == "Test Admin Title"
        assert call_args["action_url"] == "/test"
        print("[PASS] _send_notification_to_admins properly resolves admin and triggers bulk_notification")

async def test_user_transaction_notification_helper():
    from backend.data.transaksi.service import _send_transaction_notification
    from backend.auth.model import UserMap

    session = AsyncMock()
    user_uuid = uuid4()
    user_map = UserMap(
        local_user_id=str(user_uuid),
        supabase_user_id="sub-user-456"
    )

    res = MagicMock()
    res.one_or_none.return_value = user_map
    session.exec.return_value = res

    with patch("backend.db.supabse.SupabaseNotificationService.send_notification", new_callable=AsyncMock) as mock_send:
        await _send_transaction_notification(
            session=session,
            local_user_id=user_uuid,
            title="Test User Title",
            content="Test User Content",
            order_id="ORD-123",
            notif_type="order"
        )
        assert mock_send.called, "send_notification should be called for user"
        kwargs = mock_send.call_args.kwargs
        assert kwargs["user_id"] == "sub-user-456"
        assert kwargs["title"] == "Test User Title"
        assert kwargs["action_url"] == "/dashboard/orders/ORD-123"
        print("[PASS] _send_transaction_notification properly triggers send_notification")

async def test_user_service_booking_notification_helper():
    from backend.data.jasa.service import _send_service_notification
    from backend.auth.model import UserMap

    session = AsyncMock()
    user_uuid = uuid4()
    user_map = UserMap(
        local_user_id=str(user_uuid),
        supabase_user_id="sub-user-789"
    )

    res = MagicMock()
    res.one_or_none.return_value = user_map
    session.exec.return_value = res

    with patch("backend.db.supabse.SupabaseNotificationService.send_notification", new_callable=AsyncMock) as mock_send:
        await _send_service_notification(
            session=session,
            local_user_id=user_uuid,
            title="Booking Jasa Dibuat",
            content="Booking details",
            booking_number="BK-20260921-123456",
            notif_type="order"
        )
        assert mock_send.called, "send_notification should be called for booking"
        kwargs = mock_send.call_args.kwargs
        assert kwargs["user_id"] == "sub-user-789"
        assert kwargs["action_url"] == "/booking/status/BK-20260921-123456"
        print("[PASS] _send_service_notification properly triggers send_notification")

async def test_admin_promo_waybill_update_flow():
    from backend.admin.adminTransaksi.service import TransactionAdminService
    from backend.data.public.promobanner.model import PromoTransaction
    from backend.data.ongkir.model import Shipment
    from backend.auth.model import UserMap

    session = AsyncMock()
    user_uuid = uuid4()
    promo_uuid = uuid4()

    promo_trx = PromoTransaction(
        uuid=promo_uuid,
        user_id=user_uuid,
        promo_uuid=uuid4(),
        order_id="PROMO-20260921-ABCDEF12",
        items_subtotal_original=100000,
        total_discount=10000,
        items_subtotal_discounted=90000,
        shipping_cost=10000,
        service_cost=0,
        gross_amount=100000,
        transaction_status="settlement",
        has_shipment=True
    )
    
    shipment = Shipment(
        uuid=uuid4(),
        promo_transaction_uuid=promo_uuid,
        courier_name="JNE",
        courier_service="REG",
        delivery_status="PROCESSING",
        shipping_cost=10000,
        recipient_name="Budi",
        recipient_phone="08123456789",
        shipping_address="Jl. Merdeka"
    )

    user_map = UserMap(
        local_user_id=str(user_uuid),
        supabase_user_id="sub-promo-user"
    )

    # 1. promo query, 2. shipment query, 3. user_map query
    res_trx = MagicMock()
    res_trx.scalar_one_or_none.return_value = promo_trx

    res_ship = MagicMock()
    res_ship.scalar_one_or_none.return_value = shipment

    res_map = MagicMock()
    res_map.scalar_one_or_none.return_value = user_map

    session.execute.side_effect = [res_trx, res_ship, res_map]

    with patch("backend.db.supabse.SupabaseNotificationService.send_notification", new_callable=AsyncMock) as mock_send:
        result = await TransactionAdminService.update_waybill(
            session=session,
            order_id="PROMO-20260921-ABCDEF12",
            waybill_number="JNE123456789",
            courier_name="JNE",
            delivery_status="SHIPPED"
        )
        assert result == promo_trx, "update_waybill must return promo_trx for PROMO order"
        assert shipment.waybill_number == "JNE123456789"
        assert shipment.delivery_status == "SHIPPED"
        assert mock_send.called, "Must send notification to promo buyer"
        kwargs = mock_send.call_args.kwargs
        assert kwargs["user_id"] == "sub-promo-user"
        assert "JNE123456789" in kwargs["content"]
        assert kwargs["action_url"] == "/dashboard/orders/PROMO-20260921-ABCDEF12"
        print("[PASS] update_waybill handles PROMO- dual-path and notifies promo user")

async def main():
    print("=== RUNNING NOTIFICATION UNIT TESTS ===", flush=True)
    await test_admin_notification_helper()
    await test_user_transaction_notification_helper()
    await test_user_service_booking_notification_helper()
    await test_admin_promo_waybill_update_flow()
    print("=== ALL NOTIFICATION UNIT TESTS PASSED ===", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
