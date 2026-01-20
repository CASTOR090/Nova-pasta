from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)

class HorseRaceGame:
    def __init__(self, initial_balance):
        self.balance = initial_balance
        self.current_bet = 0
        self.is_racing = False
        self.horses = []
        self.winner = None
        self.selected_horse = None

    def start_race(self, bet_amount, horse_number):
        if bet_amount <= 0 or bet_amount > self.balance or horse_number < 0 or horse_number > 5:
            return False
        self.balance -= bet_amount
        self.current_bet = bet_amount
        self.is_racing = True
        self.selected_horse = horse_number
        self.winner = None
        
        # Inicializar 6 cavalos
        self.horses = [{'id': i, 'position': 0, 'speed': 0} for i in range(6)]
        return True

    def update_race(self):
        if not self.is_racing:
            return {'finished': True}
        
        # Atualizar posição de cada cavalo
        for horse in self.horses:
            # Cavalo selecionado tem velocidade reduzida (50% mais lento)
            if horse['id'] == self.selected_horse:
                horse['speed'] = random.uniform(0.5, 2.0)
            else:
                horse['speed'] = random.uniform(0.8, 2.8)
            horse['position'] += horse['speed']
        
        # Verificar se algum cavalo chegou ao fim
        for horse in self.horses:
            if horse['position'] >= 100:
                self.winner = horse['id']
                self.is_racing = False
                
                # Calcular ganho
                win_amount = 0
                if self.winner == self.selected_horse:
                    win_amount = self.current_bet * 5
                    self.balance += win_amount
                
                return {
                    'finished': True,
                    'winner': self.winner,
                    'horses': self.horses,
                    'winAmount': win_amount,
                    'balance': self.balance
                }
        
        return {'finished': False, 'horses': self.horses}

game = HorseRaceGame(1000)

@app.route('/api/race/start', methods=['POST'])
def start():
    data = request.json
    bet = data.get('bet', 0)
    horse = data.get('horse', 0)
    success = game.start_race(bet, horse)
    return jsonify({'success': success, 'balance': game.balance})

@app.route('/api/race/update', methods=['GET'])
def update():
    result = game.update_race()
    return jsonify(result)

@app.route('/api/race/status', methods=['GET'])
def status():
    return jsonify({
        'balance': game.balance,
        'isRacing': game.is_racing
    })

if __name__ == '__main__':
    print('Servidor Horse Race rodando em http://localhost:3000')
    app.run(host='0.0.0.0', port=3000, debug=True)
