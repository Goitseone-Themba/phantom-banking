from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import PaymentProvider, Payment, PaymentRefund
from .serializers import PaymentProviderSerializer, PaymentSerializer, PaymentRefundSerializer

class PaymentProviderViewSet(viewsets.ModelViewSet):
    queryset = PaymentProvider.objects.all()
    serializer_class = PaymentProviderSerializer
    permission_classes = [permissions.IsAdminUser]

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        payment = self.get_object()
        
        if payment.status not in ['pending', 'processing']:
            return Response(
                {'error': 'Only pending or processing payments can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.status = 'cancelled'
        payment.save()
        return Response(self.get_serializer(payment).data)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        
        if payment.status != 'completed':
            return Response(
                {'error': 'Only completed payments can be refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )

        refund_serializer = PaymentRefundSerializer(data={
            'payment': payment.id,
            'amount': request.data.get('amount', payment.amount),
            'reason': request.data.get('reason', 'Customer requested refund')
        })
        refund_serializer.is_valid(raise_exception=True)
        
        # Generate unique refund ID
        import uuid
        refund = refund_serializer.save(
            refund_id=f"REF-{uuid.uuid4().hex[:12].upper()}"
        )

        # Update payment status
        payment.status = 'refunded'
        payment.save()

        return Response(refund_serializer.data, status=status.HTTP_201_CREATED)

class PaymentRefundViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentRefundSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PaymentRefund.objects.all()
        return PaymentRefund.objects.filter(payment__user=self.request.user)