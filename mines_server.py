import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

class MinesGame:
    def __init__(self, initial_balance):
        self.balance = initial_balance
        self.current_bet = 0
        self.multiplier = 1.00
        self.is_playing = False
        self.board = []
        self.revealed = []
        self.mines_count = 3
        self.clicks = 0

    def start_game(self, bet_amount, mines_count):
        if bet_amount <= 0 or bet_amount > self.balance:
            return False
        self.balance -= bet_amount
        self.current_bet = bet_amount
        self.multiplier = 1.00
        self.is_playing = True
        self.mines_count = mines_count
        self.clicks = 0
        
        # Criar tabuleiro 5x5
        self.board = [0] * 25
        mines_positions = random.sample(range(25), mines_count)
        for pos in mines_positions:
            self.board[pos] = 1
        
        self.revealed = [False] * 25
        return True

    def reveal_tile(self, position):
        if not self.is_playing or self.revealed[position]:
            return {'valid': False}
        
        self.revealed[position] = True
        
        # Aumentar chance de mina: 25% de chance extra de acertar mina
        if random.random() < 0.25:
            # Força encontrar uma mina não revelada
            unrevealed_mines = [i for i in range(25) if self.board[i] == 1 and not self.revealed[i]]
            if unrevealed_mines and position not in unrevealed_mines:
                # Troca a posição atual por uma mina
                mine_pos = random.choice(unrevealed_mines)
                self.board[position], self.board[mine_pos] = self.board[mine_pos], self.board[position]
        
        is_mine = self.board[position] == 1
        
        if is_mine:
            self.is_playing = False
            return {'valid': True, 'isMine': True, 'gameOver': True, 'board': self.board}
        
        self.clicks += 1
        safe_tiles = 25 - self.mines_count
        self.multiplier = (1.0 + (self.clicks * 0.3)) * (1 + self.mines_count * 0.2)
        
        return {'valid': True, 'isMine': False, 'multiplier': self.multiplier, 'clicks': self.clicks}

    def cashout(self):
        if not self.is_playing:
            return 0
        win_amount = self.current_bet * self.multiplier
        self.balance += win_amount
        self.is_playing = False
        return win_amount

game = MinesGame(1000)

@app.route('/api/mines/start', methods=['POST'])
def start():
    data = request.json
    bet = data.get('bet', 0)
    mines = data.get('mines', 3)
    success = game.start_game(bet, mines)
    return jsonify({'success': success, 'balance': game.balance})

@app.route('/api/mines/reveal', methods=['POST'])
def reveal():
    data = request.json
    position = data.get('position', 0)
    result = game.reveal_tile(position)
    result['balance'] = game.balance
    return jsonify(result)

@app.route('/api/mines/cashout', methods=['POST'])
def cashout():
    win_amount = game.cashout()
    return jsonify({'winAmount': win_amount, 'balance': game.balance, 'board': game.board})

@app.route('/api/mines/status', methods=['GET'])
def status():
    return jsonify({
        'balance': game.balance,
        'multiplier': game.multiplier,
        'isPlaying': game.is_playing
    })

if __name__ == '__main__':
    print('Servidor Mines rodando em http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
