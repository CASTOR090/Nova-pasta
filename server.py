import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)

# Números da roleta europeia
ROULETTE_NUMBERS = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

# Cores dos números
RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

game_state = {
    'spinning': False,
    'result': None,
    'spin_start_time': None
}

@app.route('/api/spin', methods=['POST'])
def spin():
    if game_state['spinning']:
        return jsonify({'error': 'Roleta já está girando'}), 400
    
    game_state['spinning'] = True
    game_state['result'] = None
    game_state['spin_start_time'] = time.time()
    
    return jsonify({'status': 'spinning'})

@app.route('/api/result', methods=['GET'])
def get_result():
    if not game_state['spinning']:
        return jsonify({'error': 'Nenhum jogo em andamento'}), 400
    
    # Simula 3 segundos de giro
    if time.time() - game_state['spin_start_time'] < 3:
        return jsonify({'status': 'spinning'})
    
    # Gera resultado
    if game_state['result'] is None:
        number = random.choice(ROULETTE_NUMBERS)
        if number == 0:
            color = 'green'
        elif number in RED_NUMBERS:
            color = 'red'
        else:
            color = 'black'
        
        game_state['result'] = {'number': number, 'color': color}
        game_state['spinning'] = False
    
    return jsonify({
        'status': 'finished',
        'result': game_state['result']
    })

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'spinning': game_state['spinning'],
        'result': game_state['result']
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)