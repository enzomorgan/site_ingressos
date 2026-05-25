from django.urls import path

from .views import (
    DashboardHomeView,
    DashboardOrderListView,
    DashboardOrderDetailView,
    ConfirmPaymentView,
    CancelOrderView,
    DashboardLogoutView,
    DashboardEventListView,
    DashboardEventCreateView,
    DashboardEventUpdateView,
    DashboardTicketTypeListView,
    DashboardTicketTypeCreateView,
    DashboardTicketTypeUpdateView,
    CheckinSearchView,
    CheckinValidateView,
    ExportOrdersCSVView,
    ExportOrdersXLSXView,
)

app_name = "dashboard"

urlpatterns = [
    path("painel/", DashboardHomeView.as_view(), name="home"),
    path("painel/eventos/", DashboardEventListView.as_view(), name="event_list"),
    path(
        "painel/eventos/novo/", DashboardEventCreateView.as_view(), name="event_create"
    ),
    path(
        "painel/eventos/<int:pk>/editar/",
        DashboardEventUpdateView.as_view(),
        name="event_update",
    ),
    path(
        "painel/eventos/<int:event_pk>/ingressos/",
        DashboardTicketTypeListView.as_view(),
        name="ticket_type_list",
    ),
    path(
        "painel/eventos/<int:event_pk>/ingressos/novo/",
        DashboardTicketTypeCreateView.as_view(),
        name="ticket_type_create",
    ),
    path(
        "painel/ingressos/<int:pk>/editar/",
        DashboardTicketTypeUpdateView.as_view(),
        name="ticket_type_update",
    ),
    path("painel/pedidos/", DashboardOrderListView.as_view(), name="order_list"),
    path(
        "painel/pedidos/exportar-csv/",
        ExportOrdersCSVView.as_view(),
        name="export_orders_csv",
    ),
    path(
        "painel/pedidos/exportar-xlsx/",
        ExportOrdersXLSXView.as_view(),
        name="export_orders_xlsx",
    ),
    path(
        "painel/pedidos/<int:pk>/",
        DashboardOrderDetailView.as_view(),
        name="order_detail",
    ),
    path(
        "painel/pedidos/<int:pk>/confirmar-pagamento/",
        ConfirmPaymentView.as_view(),
        name="confirm_payment",
    ),
    path(
        "painel/pedidos/<int:pk>/cancelar/",
        CancelOrderView.as_view(),
        name="cancel_order",
    ),
    path('painel/checkin/', CheckinSearchView.as_view(), name='checkin_search'),
    path('painel/checkin/<uuid:code>/', CheckinValidateView.as_view(), name='checkin_validate'),
    path("painel/sair/", DashboardLogoutView.as_view(), name="logout"),
]
