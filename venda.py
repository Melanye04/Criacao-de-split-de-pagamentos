import requests
URL = "http://127.0.0.1:8000/v1/checkout"

venda = {
    "valor": 200.0,
    "prestador_gateway_id": "whsec_7c462a465ee1e8c53a474d9b48cb56a4b3e3b377f9ccdc1fa3224320c04247e2"
}

print(f"Enviando venda de R$ {venda['valor']}...")

try:
    response = requests.post(URL, json=venda)
    if response.status_code ==200:
        print("Sucesso!")
        print(f"Resposta do Servidor: {response.json()}")
    else:
        print(f"Erro {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Não foi possível conectar ao servidor: {e}")