from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

class BlackjackGame:
    def __init__(self, initial_balance):
        self.balance = initial_balance
        self.current_bet = 0
        self.player_hand = []
        self.dealer_hand = []
        self.deck = []
        self.is_playing = False

    def create_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.deck = [{'value': v, 'suit': s} for s in suits for v in values]
        random.shuffle(self.deck)

    def card_value(self, card):
        if card['value'] in ['J', 'Q', 'K']:
            return 10
        elif card['value'] == 'A':
            return 11
        else:
            return int(card['value'])

    def calculate_hand(self, hand):
        total = sum(self.card_value(card) for card in hand)
        aces = sum(1 for card in hand if card['value'] == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def start_game(self, bet_amount):
        if bet_amount <= 0 or bet_amount > self.balance:
            return False
        
        self.balance -= bet_amount
        self.current_bet = bet_amount
        self.is_playing = True
        self.create_deck()
        
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        
        return True

    def hit(self):
        if not self.is_playing:
            return None
        self.player_hand.append(self.deck.pop())
        player_total = self.calculate_hand(self.player_hand)
        
        if player_total > 21:
            self.is_playing = False
            return {'busted': True, 'player_total': player_total}
        
        return {'busted': False, 'player_total': player_total}

    def stand(self):
        if not self.is_playing:
            return None
        
        while self.calculate_hand(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())
        
        player_total = self.calculate_hand(self.player_hand)
        dealer_total = self.calculate_hand(self.dealer_hand)
        
        self.is_playing = False
        
        if dealer_total > 21 or player_total > dealer_total:
            win_amount = self.current_bet * 2
            self.balance += win_amount
            return {'won': True, 'player_total': player_total, 'dealer_total': dealer_total, 'win_amount': win_amount}
        elif player_total == dealer_total:
            self.balance += self.current_bet
            return {'won': None, 'player_total': player_total, 'dealer_total': dealer_total, 'win_amount': self.current_bet}
        else:
            return {'won': False, 'player_total': player_total, 'dealer_total': dealer_total, 'win_amount': 0}

game = BlackjackGame(1000)

@app.route('/api/blackjack/start', methods=['POST'])
def start():
    data = request.json
    bet = data.get('bet', 0)
    success = game.start_game(bet)
    
    if success:
        return jsonify({
            'success': True,
            'balance': game.balance,
            'player_hand': game.player_hand,
            'dealer_hand': [game.dealer_hand[0]],
            'player_total': game.calculate_hand(game.player_hand)
        })
    return jsonify({'success': False})

@app.route('/api/blackjack/hit', methods=['POST'])
def hit():
    result = game.hit()
    if result:
        return jsonify({
            'player_hand': game.player_hand,
            'player_total': result['player_total'],
            'busted': result['busted'],
            'balance': game.balance
        })
    return jsonify({'error': 'Game not active'})

@app.route('/api/blackjack/stand', methods=['POST'])
def stand():
    result = game.stand()
    if result:
        return jsonify({
            'player_hand': game.player_hand,
            'dealer_hand': game.dealer_hand,
            'player_total': result['player_total'],
            'dealer_total': result['dealer_total'],
            'won': result['won'],
            'win_amount': result['win_amount'],
            'balance': game.balance
        })
    return jsonify({'error': 'Game not active'})

@app.route('/api/blackjack/status', methods=['GET'])
def status():
    return jsonify({
        'balance': game.balance,
        'is_playing': game.is_playing
    })

if __name__ == '__main__':
    print('Servidor Blackjack rodando em http://localhost:7000')
    app.run(host='0.0.0.0', port=7000, debug=False)
