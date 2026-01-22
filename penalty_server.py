import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

class PenaltyGame:
    def __init__(self, initial_balance):
        self.balance = initial_balance
        self.current_bet = 0

    def shoot(self, bet_amount, player_position):
        if bet_amount <= 0 or bet_amount > self.balance:
            return {'success': False}
        
        self.balance -= bet_amount
        self.current_bet = bet_amount
        
        # Aumentar chance de defesa: 45% de chance do goleiro pegar
        if random.random() < 0.45:
            goalkeeper_position = player_position  # Goleiro vai na mesma direção
        else:
            goalkeeper_position = random.randint(0, 2)
        
        scored = player_position != goalkeeper_position
        
        win_amount = 0
        if scored:
            win_amount = bet_amount * 3
            self.balance += win_amount
        
        return {
            'success': True,
            'scored': scored,
            'playerPosition': player_position,
            'goalkeeperPosition': goalkeeper_position,
            'winAmount': win_amount,
            'balance': self.balance
        }

    def get_status(self):
        return {'balance': self.balance}

game = PenaltyGame(1000)

@app.route('/api/penalty/shoot', methods=['POST'])
def shoot():
    data = request.json
    bet = data.get('bet', 0)
    position = data.get('position', 0)
    result = game.shoot(bet, position)
    return jsonify(result)

@app.route('/api/penalty/status', methods=['GET'])
def status():
    return jsonify(game.get_status())

if __name__ == '__main__':
    print('Servidor Penalty rodando em http://localhost:4000')
    app.run(host='0.0.0.0', port=4000, debug=True)
