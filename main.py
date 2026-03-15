import os
import stripe
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
# importe os schmas 
from split import PedidoSchema # type: ignore

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI()

# LOGICA DE CÁLCULO
class SplitService:
    @staticmethod
    def calcular_divisao(valor_venda: float, percentual_comissao: float, taxa_fixa: float):
        comissao = (valor_venda * (percentual_comissao / 100)) + taxa_fixa
        valor_fornecedor = valor_venda - comissao
        return {
            "total": valor_venda,
            "comissao_plataforma": round(comissao, 2),
            "valor_fornecedor": round(valor_fornecedor, 2)
        }


def criar_pagamento_com_split(valor: float, prestador_stripe_id: str, dados_split: dict):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(valor * 100),
            currency="brl",
            payment_method_types=["card"],
            transfer_data={
                "amount": int(dados_split["valor_fornecedor"] * 100),
                "destination": prestador_stripe_id, 
            },
        )
        return intent
    except Exception as e:
        print(f"Erro no Gateway: {e}")
        return None

def salvar_split_no_banco(id, divisao, fornecedor_id):
    print(f"Salvando no banco: {id}")


@app.get("/")
def home():
    return {"status": "Servidor Online"}

@app.post("/v1/checkout")
async def checkout(pedido: PedidoSchema):
    divisao = SplitService.calcular_divisao(
        valor_venda=pedido.valor,
        percentual_comissao=10.0,
        taxa_fixa=0.50
    )

    resultado = criar_pagamento_com_split(
        valor=pedido.valor,
        prestador_stripe_id=pedido.prestador_gateway_id, 
        dados_split=divisao
    )

    if resultado:
        salvar_split_no_banco(resultado.id, divisao, pedido.prestador_gateway_id)
        return {'client_secret': resultado.client_secret}
    
    raise HTTPException(status_code=400, detail="Erro ao processar split")

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        
        if event['type'] == 'payment_intent.succeeded':
            print("Pagamento bem sucedido!")
            
        elif event['type'] == 'transfer.created':
            print("Split realizado com sucesso!")

        return {"status": "success"}
    except Exception as e:
        print(f"Erro no Webhook: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)