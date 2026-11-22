"""Notifikasi realtime lokal — menggantikan Supabase Realtime + PostgREST."""

from backend.user.notifications.service import (
    notify_user,
    notify_users,
    list_for_user,
    count_unread,
    mark_read,
    mark_all_read,
    delete_notification,
)

__all__ = [
    "notify_user",
    "notify_users",
    "list_for_user",
    "count_unread",
    "mark_read",
    "mark_all_read",
    "delete_notification",
]
