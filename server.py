from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

class AviatorGame:
    def __init__(self, initial_balance):
        self.balance = initial_balance
        self.current_bet = 0
        self.multiplier = 1.00
        self.is_playing = False
        self.crash_point = 0

    def start_game(self, bet_amount):
        if bet_amount <= 0 or bet_amount > self.balance:
            return False
        self.balance -= bet_amount
        self.current_bet = bet_amount
        self.multiplier = 1.00
        self.is_playing = True
        # Aumentar chance de crash cedo: 55% entre 1.1x-1.8x, 45% entre 1.8x-2.6x
        if random.random() < 0.55:
            self.crash_point = 1.1 + random.random() * 0.7  # 1.1x a 1.8x
        else:
            self.crash_point = 1.8 + random.random() * 0.8  # 1.8x a 2.6x
        return True

    def update_multiplier(self):
        if self.is_playing:
            self.multiplier += 0.01

    def check_crash(self):
        return self.multiplier >= self.crash_point

    def cashout(self):
        if not self.is_playing:
            return 0
        win_amount = self.current_bet * self.multiplier
        self.balance += win_amount
        self.is_playing = False
        return win_amount

    def crash(self):
        self.is_playing = False

game = AviatorGame(1000)

@app.route('/api/start', methods=['POST'])
def start():
    data = request.json
    bet = data.get('bet', 0)
    success = game.start_game(bet)
    return jsonify({'success': success, 'balance': game.balance})

@app.route('/api/update', methods=['GET'])
def update():
    game.update_multiplier()
    crashed = game.check_crash()
    if crashed:
        game.crash()
    return jsonify({
        'multiplier': game.multiplier,
        'crashed': crashed,
        'isPlaying': game.is_playing,
        'balance': game.balance
    })

@app.route('/api/cashout', methods=['POST'])
def cashout():
    win_amount = game.cashout()
    return jsonify({'winAmount': win_amount, 'balance': game.balance})

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'balance': game.balance,
        'multiplier': game.multiplier,
        'isPlaying': game.is_playing
    })

if __name__ == '__main__':
    print('Servidor rodando em http://localhost:8080')
    app.run(host='0.0.0.0', port=8080, debug=True)
