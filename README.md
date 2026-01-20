# Jogo Aviator - Python + JavaScript

## Arquitetura
- **Backend**: Python Flask (servidor HTTP REST API)
- **Frontend**: HTML + JavaScript (cliente)

## Arquivos
- `server.py` - Servidor Flask com lógica do jogo
- `index.html` - Interface do usuário
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

- `POST /api/start` - Iniciar jogo
- `GET /api/update` - Atualizar multiplicador
- `POST /api/cashout` - Sacar ganhos
- `GET /api/status` - Status do jogo

## Como jogar
1. Inicie o servidor Python: `python server.py`
2. Abra `index.html` no navegador
3. Digite o valor da aposta
4. Clique em APOSTAR
5. Clique em SACAR antes do crash!
