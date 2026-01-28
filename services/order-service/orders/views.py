import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction as db_transaction
from django.db.models import Q
from django.utils import timezone

from .models import Order, Transaction, Wallet
from .serializers import OrderSerializer, CreateOrderPayload
from .abacatepay import AbacatePayService
from .catalog_client import CatalogClient
from .finance import FinanceCalculator

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra os pedidos:
        - Admin vê tudo.
        - Usuário vê apenas o que comprou (client) ou o que vendeu (freelancer).
        """
        user_id = self.request.user.id
        if self.request.user.is_staff:
            return Order.objects.all()

        return Order.objects.filter(
            Q(client_id=user_id) | Q(freelancer_id=user_id)
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """
        Cria um novo pedido com validação de catálogo e split financeiro.
        """
        # 1. Validação dos dados de entrada
        payload = CreateOrderPayload(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data

        try:
            # 2. Validação Externa (Catalog Service)
            gig_data = CatalogClient.get_gig_details(data['gig_id'])

            if gig_data.get('status') != 'ATIVO':
                return Response(
                    {"error": "Este Gig não está disponível para venda no momento."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            CatalogClient.validate_price(gig_data, data['amount'])

            # 3. Cálculo Financeiro (Split de Taxas)
            finance = FinanceCalculator.calculate_fees(data['amount'])

        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Criação do Pedido (Banco de Dados + Gateway)
        try:
            with db_transaction.atomic():
                # A. Salva o Pedido
                # CORREÇÃO: Chaves alinhadas com o novo retorno do FinanceCalculator
                order = Order.objects.create(
                    client_id=request.user.id,
                    freelancer_id=data['freelancer_id'],
                    gig_id=data['gig_id'],
                    package_title=f"{gig_data.get('titulo', 'Gig')} (Snapshot)",

                    # Valores Financeiros (Split)
                    amount=finance['total_amount'],
                    platform_fee=finance['platform_fee'],
                    freelancer_net=finance['freelancer_net'],
                    gateway_fee=finance['gateway_cost'],

                    status='PENDING'
                )

                # B. Chama o Gateway (AbacatePay)
                customer_data = {
                    'name': data['customer_name'],
                    'email': data['customer_email'],
                    'taxId': data['customer_cpf']  # Abacate usa taxId
                }

                abacate = AbacatePayService()
                billing_data = abacate.create_billing(order, customer_data)

                # C. Registra a Transação
                Transaction.objects.create(
                    order=order,
                    external_id=billing_data.get('id'),  # ID do Billing
                    payment_url=billing_data.get('url'),
                    status='PENDING'
                )

                # D. Cria/Atualiza Wallet do Vendedor (Saldo Bloqueado)
                # O dinheiro "entra" no sistema, mas fica pendente
                wallet, _ = Wallet.objects.get_or_create(user_id=data['freelancer_id'])
                wallet.credit_pending(finance['freelancer_net'])

                return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao processar pedido: {str(e)}")
            return Response(
                {"error": "Erro interno ao processar pagamento.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='deliver')
    def deliver_order(self, request, pk=None):
        """
        Ação para o Freelancer entregar o trabalho.
        """
        order = self.get_object()

        if str(order.freelancer_id) != str(request.user.id):
            return Response({"error": "Acesso negado. Apenas o freelancer responsável pode entregar."}, status=403)

        if order.status != 'IN_PROGRESS':
            return Response({"error": "O pedido precisa estar pago e em andamento para ser entregue."}, status=400)

        files = request.data.get('delivery_files')
        note = request.data.get('delivery_note', '')

        if not files:
            return Response({"error": "O link dos arquivos é obrigatório para realizar a entrega."}, status=400)

        order.delivery_files = files
        order.delivery_note = note
        order.status = 'DELIVERED'
        order.delivered_at = timezone.now()
        order.save()

        return Response({"status": "DELIVERED", "message": "Trabalho entregue com sucesso!"})

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_order(self, request, pk=None):
        """
        Ação para o Cliente aceitar e concluir o pedido.
        Libera o dinheiro na Wallet.
        """
        order = self.get_object()

        if str(order.client_id) != str(request.user.id):
            return Response({"error": "Acesso negado. Apenas o cliente pode finalizar o pedido."}, status=403)

        if order.status != 'DELIVERED':
            return Response({"error": "O pedido precisa ter sido entregue pelo freelancer antes de concluir."},
                            status=400)

        # Transação Atômica para garantir que se o saldo não liberar, o pedido não completa
        with db_transaction.atomic():
            order.status = 'COMPLETED'
            order.completed_at = timezone.now()
            order.save()

            # Libera o saldo na carteira
            try:
                wallet = Wallet.objects.get(user_id=order.freelancer_id)
                wallet.release_funds(order.freelancer_net)
            except Wallet.DoesNotExist:
                # Caso extremo: Wallet não existe (não deveria acontecer se criado no create)
                # Recria e força saldo disponível (ajuste manual do sistema)
                wallet = Wallet.objects.create(user_id=order.freelancer_id)
                # Como não estava pending (erro), adicionamos direto no available
                wallet.available_balance += order.freelancer_net
                wallet.save()
                logger.warning(f"Wallet recriada forçadamente para usuário {order.freelancer_id} no pedido {order.id}")

        return Response({"status": "COMPLETED", "message": "Pedido concluído! O valor foi liberado para o freelancer."})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='webhook')
    def webhook(self, request):
        """
        Recebe notificações do AbacatePay.
        """
        event = request.data.get('event')
        data = request.data.get('data', {})
        bill_id = data.get('id')

        logger.info(f"Webhook recebido: {event} - ID: {bill_id}")

        if event == 'billing.paid' and bill_id:
            try:
                # Busca a transação
                tx = Transaction.objects.get(external_id=bill_id)

                if tx.status != 'PAID':
                    with db_transaction.atomic():
                        tx.status = 'PAID'
                        tx.save()

                        order = tx.order
                        if order.status == 'PENDING':
                            order.status = 'IN_PROGRESS'
                            order.save()
                            logger.info(f"Pedido {order.id} pago e iniciado.")

            except Transaction.DoesNotExist:
                logger.warning(f"Transação não encontrada para Billing ID: {bill_id}")
                pass

        return Response({"received": True})