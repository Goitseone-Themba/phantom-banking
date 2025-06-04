from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import Transaction, TransactionFee
from .serializers import TransactionSerializer, TransactionFeeSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(
            Q(user=user) | 
            Q(source_account__in=user.wallets.values_list('wallet_id', flat=True)) |
            Q(destination_account__in=user.wallets.values_list('wallet_id', flat=True))
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        transaction = self.get_object()
        
        if transaction.status != 'pending':
            return Response(
                {'error': 'Only pending transactions can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        transaction.status = 'cancelled'
        transaction.save()
        return Response(self.get_serializer(transaction).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def complete(self, request, pk=None):
        transaction = self.get_object()
        
        if transaction.status != 'pending':
            return Response(
                {'error': 'Only pending transactions can be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        transaction.status = 'completed'
        transaction.completed_at = timezone.now()
        transaction.save()

        # Create transaction fee if provided
        fee_data = request.data.get('fee')
        if fee_data:
            TransactionFee.objects.create(
                transaction=transaction,
                amount=fee_data.get('amount'),
                description=fee_data.get('description', 'Transaction fee')
            )

        return Response(self.get_serializer(transaction).data)