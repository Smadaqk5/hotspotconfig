"""
URL configuration for tickets app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TicketTypeViewSet, TicketViewSet, TicketSaleViewSet, 
    TicketBatchViewSet, TicketUsageViewSet
)

router = DefaultRouter()
router.register(r'ticket-types', TicketTypeViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'sales', TicketSaleViewSet)
router.register(r'batches', TicketBatchViewSet)
router.register(r'usage', TicketUsageViewSet)

urlpatterns = [
    path('api/tickets/', include(router.urls)),
]
