import os
from abacatepay import AbacatePay  # SDK oficial
from .finance import FinanceCalculator


class AbacatePayService:
    def __init__(self):
        self.api_key = os.environ.get('ABACATEPAY_API_KEY', '')
        # Inicializa o cliente do SDK
        self.client = AbacatePay(self.api_key)

    def create_billing(self, order, customer_data):
        """
        Cria uma cobrança Pix usando o SDK do AbacatePay.
        """
        if not self.api_key or self.api_key == "dummy_key":
            return self._mock_response(order)

        try:
            # 1. Calculamos o Split (apenas para registro interno ou metadata por enquanto)
            # O AbacatePay receberá o valor CHEIO do cliente.
            fees = FinanceCalculator.calculate_fees(order.amount)

            # 2. Prepara os dados conforme o SDK espera
            # Convertemos o pedido em um "Produto" para aparecer bonito na fatura
            amount_in_cents = int(order.amount * 100)

            billing = self.client.billing.create(
                frequency="ONE_TIME",
                methods=["PIX"],
                products=[
                    {
                        "externalId": str(order.service.id),  # ID do Gig
                        "name": f"Serviço: {order.service.title}",
                        "quantity": 1,
                        "price": amount_in_cents,
                        "description": f"Pedido #{order.id} via Lykos"
                    }
                ],
                customer={
                    "name": customer_data.get('name'),
                    "email": customer_data.get('email'),
                    "taxId": customer_data.get('taxId', '00000000000')  # CPF/CNPJ
                },
                returnURL=f"https://lykos.com.br/u/orders/{order.id}",  # Redirecionamento pós-pagamento
                completionUrl=f"https://api.lykos.com.br/api/v1/webhooks/abacatepay"  # Webhook
            )

            # O SDK retorna um objeto Billing, acessamos os dados dele
            return {
                "id": billing.data.id,
                "url": billing.data.url,
                "status": billing.data.status
            }

        except Exception as e:
            # Log de erro real seria ideal aqui
            print(f"Erro ao criar cobrança AbacatePay: {str(e)}")
            raise e

    def _mock_response(self, order):
        """Simula resposta para ambiente de dev sem API Key"""
        import uuid
        fake_id = f"bill_{uuid.uuid4().hex[:10]}"
        return {
            "id": fake_id,
            "url": f"https://abacatepay.com/pay/simulado/{fake_id}",
            "status": "PENDING"
        }