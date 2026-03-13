from django.contrib import admin
from .models import Event, TicketType


class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'date',
        'location',
        'active'
    )

    prepopulated_fields = {"slug": ("title",)}

    inlines = [TicketTypeInline]


admin.site.register(TicketType)