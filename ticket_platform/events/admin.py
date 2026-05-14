from django.contrib import admin

from .models import Event, TicketType


class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1
    fields = (
        "name",
        "price",
        "quantity",
        "sold",
    )
    readonly_fields = ("sold",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "date",
        "location",
        "active",
        "created_by",
        "created_at",
    )

    list_filter = (
        "active",
        "date",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "location",
    )

    prepopulated_fields = {"slug": ("title",)}

    readonly_fields = ("created_at",)

    inlines = [TicketTypeInline]


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "name",
        "price",
        "quantity",
        "sold",
        "available",
    )

    list_filter = ("event",)

    search_fields = (
        "name",
        "event__title",
    )

    readonly_fields = ("sold",)
