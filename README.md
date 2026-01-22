# Roleta Europeia - Python + JavaScript

## Arquitetura
- **Backend**: Python Flask (servidor HTTP REST API)
- **Frontend**: HTML + JavaScript (cliente)

## Arquivos
- `server.py` - Servidor Flask com lógica da roleta
- `index.html` - Interface da roleta
- `requirements.txt` - Dependências Python

## Como executar

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor
python server.py

# Abrir index.html no navegador
```

## Endpoints da API

- `POST /api/spin` - Girar a roleta
- `GET /api/result` - Obter resultado do giro
- `GET /api/status` - Status da roleta

## Como jogar
1. Inicie o servidor Python: `python server.py`
2. Abra `index.html` no navegador
3. Digite o valor da aposta
4. Selecione o tipo de aposta (vermelho, preto, verde, par, ímpar, 1-18)
5. Clique em GIRAR ROLETA
6. Aguarde o resultado!
