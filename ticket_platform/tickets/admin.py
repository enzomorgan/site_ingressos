from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "order",
        "checked_in",
        "created_at",
    )

    list_filter = (
        "checked_in",
        "created_at",
    )

    search_fields = (
        "code",
        "order__user__username",
        "order__user__email",
    )

    readonly_fields = (
        "code",
        "qr_code",
        "pdf_file",
        "created_at",
    )
