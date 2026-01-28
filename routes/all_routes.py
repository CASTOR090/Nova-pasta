from flask import Blueprint, jsonify, request
import sqlite3
import random
import time

# Blueprint único para todos os endpoints
casino_bp = Blueprint('casino', __name__, url_prefix='/api')

# Endpoint de teste
@casino_bp.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'OK', 'message': 'Servidor funcionando!'})

# Função para conectar ao banco
def get_db_connection():
    return sqlite3.connect('../casino.db')

# ==================== GERENCIADOR DE SALDO ÚNICO ====================
class SaldoManager:
    @staticmethod
    def get_saldo(usuario_id=1):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT saldo FROM usuarios WHERE id = ?', (usuario_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 1000.0
    
    @staticmethod
    def update_saldo(novo_saldo, usuario_id=1):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE usuarios SET saldo = ? WHERE id = ?', 
                      (novo_saldo, usuario_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def subtrair_aposta(valor, usuario_id=1):
        saldo_atual = SaldoManager.get_saldo(usuario_id)
        if valor <= saldo_atual:
            novo_saldo = saldo_atual - valor
            SaldoManager.update_saldo(novo_saldo, usuario_id)
            return True
        return False
    
    @staticmethod
    def adicionar_ganho(valor, usuario_id=1):
        saldo_atual = SaldoManager.get_saldo(usuario_id)
        novo_saldo = saldo_atual + valor
        SaldoManager.update_saldo(novo_saldo, usuario_id)

# ==================== CONFIGURAÇÕES ====================
ROULETTE_NUMBERS = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

# Estados dos jogos
roulette_state = {'spinning': False, 'result': None, 'bet_info': None}

# ==================== CLASSES DOS JOGOS ====================
class BlackjackGame:
    def __init__(self):
        self.current_bet = 0
        self.player_hand = []
        self.dealer_hand = []
        self.deck = []
        self.is_playing = False

    @property
    def balance(self):
        return SaldoManager.get_saldo()

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
        
        if not SaldoManager.subtrair_aposta(bet_amount):
            return False
            
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
            SaldoManager.adicionar_ganho(win_amount)
            return {'won': True, 'player_total': player_total, 'dealer_total': dealer_total, 'win_amount': win_amount}
        elif player_total == dealer_total:
            SaldoManager.adicionar_ganho(self.current_bet)  # Devolve aposta
            return {'won': None, 'player_total': player_total, 'dealer_total': dealer_total, 'win_amount': self.current_bet}
        else:
            return {'won': False, 'player_total': player_total, 'dealer_total': dealer_total, 'win_amount': 0}

class MinesGame:
    def __init__(self):
        self.current_bet = 0
        self.multiplier = 1.00
        self.is_playing = False
        self.board = []
        self.revealed = []
        self.mines_count = 3
        self.clicks = 0

    @property
    def balance(self):
        return SaldoManager.get_saldo()

    def start_game(self, bet_amount, mines_count):
        if bet_amount <= 0 or bet_amount > self.balance:
            return False
            
        if not SaldoManager.subtrair_aposta(bet_amount):
            return False
            
        self.current_bet = bet_amount
        self.multiplier = 1.00
        self.is_playing = True
        self.mines_count = mines_count
        self.clicks = 0
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
        is_mine = self.board[position] == 1
        if is_mine:
            self.is_playing = False
            return {'valid': True, 'isMine': True, 'gameOver': True, 'board': self.board}
        self.clicks += 1
        self.multiplier = (1.0 + (self.clicks * 0.3)) * (1 + self.mines_count * 0.2)
        return {'valid': True, 'isMine': False, 'multiplier': self.multiplier, 'clicks': self.clicks}

    def cashout(self):
        if not self.is_playing:
            return 0
        win_amount = self.current_bet * self.multiplier
        SaldoManager.adicionar_ganho(win_amount)
        self.is_playing = False
        return win_amount

class PenaltyGame:
    def __init__(self):
        pass

    @property
    def balance(self):
        return SaldoManager.get_saldo()

    def shoot(self, bet_amount, player_position):
        if bet_amount <= 0 or bet_amount > self.balance:
            return {'success': False}
            
        if not SaldoManager.subtrair_aposta(bet_amount):
            return {'success': False}
            
        if random.random() < 0.45:
            goalkeeper_position = player_position
        else:
            goalkeeper_position = random.randint(0, 2)
        scored = player_position != goalkeeper_position
        win_amount = 0
        if scored:
            win_amount = bet_amount * 3
            SaldoManager.adicionar_ganho(win_amount)
        return {
            'success': True,
            'scored': scored,
            'playerPosition': player_position,
            'goalkeeperPosition': goalkeeper_position,
            'winAmount': win_amount,
            'balance': self.balance
        }

class HorseRaceGame:
    def __init__(self):
        self.current_bet = 0
        self.is_racing = False
        self.horses = []
        self.winner = None
        self.selected_horse = None

    @property
    def balance(self):
        return SaldoManager.get_saldo()

    def start_race(self, bet_amount, horse_number):
        if bet_amount <= 0 or bet_amount > self.balance or horse_number < 0 or horse_number > 5:
            return False
            
        if not SaldoManager.subtrair_aposta(bet_amount):
            return False
            
        self.current_bet = bet_amount
        self.is_racing = True
        self.selected_horse = horse_number
        self.winner = None
        self.horses = [{'id': i, 'position': 0, 'speed': 0} for i in range(6)]
        return True

    def update_race(self):
        if not self.is_racing:
            return {'finished': True}
        for horse in self.horses:
            if horse['id'] == self.selected_horse:
                horse['speed'] = random.uniform(0.5, 2.0)
            else:
                horse['speed'] = random.uniform(0.8, 2.8)
            horse['position'] += horse['speed']
        for horse in self.horses:
            if horse['position'] >= 100:
                self.winner = horse['id']
                self.is_racing = False
                win_amount = 0
                if self.winner == self.selected_horse:
                    win_amount = self.current_bet * 5
                    SaldoManager.adicionar_ganho(win_amount)
                return {
                    'finished': True,
                    'winner': self.winner,
                    'horses': self.horses,
                    'winAmount': win_amount,
                    'balance': self.balance
                }
        return {'finished': False, 'horses': self.horses}

class AviatorGame:
    def __init__(self):
        self.current_bet = 0
        self.multiplier = 1.00
        self.is_flying = False
        self.crash_point = 0

    @property
    def balance(self):
        return SaldoManager.get_saldo()

    def start_flight(self, bet_amount):
        if bet_amount <= 0 or bet_amount > self.balance:
            return False
            
        if not SaldoManager.subtrair_aposta(bet_amount):
            return False
            
        self.current_bet = bet_amount
        self.is_flying = True
        
        # Definir multiplicador e crash instantaneamente
        random_val = random.random()
        if random_val < 0.55:
            self.crash_point = 1.1 + random.random() * 0.7  # 1.1x - 1.8x
        else:
            self.crash_point = 1.8 + random.random() * 1.2  # 1.8x - 3.0x
        
        # Definir multiplicador aleatório entre 1.0 e crash_point
        self.multiplier = 1.0 + random.random() * (self.crash_point - 1.0)
        return True

    def get_status(self):
        if not self.is_flying:
            return {'flying': False, 'multiplier': self.multiplier, 'crashed': False}
        
        # Verificar se crashou instantaneamente
        if self.multiplier >= self.crash_point:
            self.is_flying = False
            return {'flying': False, 'multiplier': self.multiplier, 'crashed': True}
            
        return {'flying': True, 'multiplier': self.multiplier, 'crashed': False}

    def cashout(self):
        if not self.is_flying:
            return 0
            
        win_amount = self.current_bet * self.multiplier
        SaldoManager.adicionar_ganho(win_amount)
        self.is_flying = False
        return win_amount

class DiceGame:
    def __init__(self):
        pass

    @property
    def balance(self):
        return SaldoManager.get_saldo()

    def roll_dice(self, bet_amount, bet_type):
        if bet_amount <= 0 or bet_amount > self.balance:
            return {'success': False, 'message': 'Aposta inválida'}
            
        if not SaldoManager.subtrair_aposta(bet_amount):
            return {'success': False, 'message': 'Saldo insuficiente'}
            
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2
        
        won = False
        multiplier = 0
        
        if bet_type == 'baixo':
            won = 2 <= total <= 6
            multiplier = 2
        elif bet_type == 'sete':
            won = total == 7
            multiplier = 5
        elif bet_type == 'alto':
            won = 8 <= total <= 12
            multiplier = 2
        elif bet_type == 'par':
            won = total % 2 == 0
            multiplier = 2
        elif bet_type == 'dupla':
            won = dice1 == dice2
            multiplier = 6
        elif bet_type == 'impar':
            won = total % 2 == 1
            multiplier = 2
        
        win_amount = 0
        if won:
            win_amount = bet_amount * multiplier
            SaldoManager.adicionar_ganho(win_amount)
        
        return {
            'success': True,
            'dice1': dice1,
            'dice2': dice2,
            'total': total,
            'won': won,
            'winAmount': win_amount,
            'balance': self.balance
        }

class SlotsGame:
    def __init__(self):
        self.symbols = ['🍒', '🍋', '🍊', '🍇', '🔔', '💎', '7️⃣']

    @property
    def balance(self):
        return SaldoManager.get_saldo()

    def spin(self, bet_amount):
        if bet_amount <= 0 or bet_amount > self.balance:
            return {'success': False, 'message': 'Aposta inválida'}
            
        if not SaldoManager.subtrair_aposta(bet_amount):
            return {'success': False, 'message': 'Saldo insuficiente'}
        
        # Resultado com probabilidades
        rand = random.random()
        if rand < 0.02:  # 2% - Jackpot
            result = ['💎', '💎', '💎']
            multiplier = 50
        elif rand < 0.05:  # 3% - 3 iguais especiais
            result = ['7️⃣', '7️⃣', '7️⃣']
            multiplier = 25
        elif rand < 0.15:  # 10% - 3 iguais normais
            symbol = random.choice(self.symbols[:5])
            result = [symbol, symbol, symbol]
            multiplier = 10
        elif rand < 0.30:  # 15% - 2 iguais
            symbol = random.choice(self.symbols)
            result = [symbol, symbol, random.choice(self.symbols)]
            while result[2] == symbol:
                result[2] = random.choice(self.symbols)
            multiplier = 2
        else:  # 70% - Perder
            result = [random.choice(self.symbols) for _ in range(3)]
            while result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
                result = [random.choice(self.symbols) for _ in range(3)]
            multiplier = 0
        
        win_amount = bet_amount * multiplier if multiplier > 0 else 0
        if win_amount > 0:
            SaldoManager.adicionar_ganho(win_amount)
        
        return {
            'success': True,
            'result': result,
            'winAmount': win_amount,
            'balance': self.balance
        }

# Instâncias dos jogos
blackjack_game = BlackjackGame()
mines_game = MinesGame()
penalty_game = PenaltyGame()
race_game = HorseRaceGame()
aviator_game = AviatorGame()
dice_game = DiceGame()
slots_game = SlotsGame()

# ==================== ENDPOINTS DE AUTENTICAÇÃO ====================
@casino_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, saldo FROM usuarios WHERE email = ? AND senha = ?', (email, senha))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return jsonify({
                'message': 'Login realizado com sucesso',
                'user_id': user[0],
                'nome': user[1],
                'saldo': user[2]
            })
        else:
             return jsonify({'error': 'Email ou senha inválidos'}), 401
             
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@casino_bp.route('/cadastro', methods=['POST'])
def cadastro():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')
        
        if not nome or not email or not senha:
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO usuarios (nome, email, senha, saldo) VALUES (?, ?, ?, ?)', 
                           (nome, email, senha, 1000.0))
            conn.commit()
            conn.close()
            return jsonify({'message': 'Usuário cadastrado com sucesso'})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'error': 'Email já cadastrado'}), 409
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# ==================== ENDPOINTS DA ROLETA ====================
@casino_bp.route('/spin', methods=['POST'])
def spin():
    if roulette_state['spinning']:
        return jsonify({'error': 'Roleta já está girando'}), 400
    
    data = request.get_json() or {}
    bet_type = data.get('bet_type')
    bet_amount = data.get('bet_amount', 0)
    
    # Verificar se tem saldo suficiente
    if bet_amount <= 0 or bet_amount > SaldoManager.get_saldo():
        return jsonify({'error': 'Saldo insuficiente'}), 400
    
    # Subtrair aposta
    if not SaldoManager.subtrair_aposta(bet_amount):
        return jsonify({'error': 'Erro ao processar aposta'}), 400
    
    roulette_state['spinning'] = True
    roulette_state['result'] = None
    roulette_state['bet_info'] = {'type': bet_type, 'amount': bet_amount}
    
    return jsonify({'status': 'spinning'})

@casino_bp.route('/result', methods=['GET'])
def get_result():
    if not roulette_state['spinning']:
        return jsonify({'error': 'Nenhum jogo em andamento'}), 400
    
    if roulette_state['result'] is None:
        number = random.choice(ROULETTE_NUMBERS)
        if number == 0:
            color = 'green'
        elif number in RED_NUMBERS:
            color = 'red'
        else:
            color = 'black'
        
        # Calcular ganho
        bet_info = roulette_state['bet_info']
        if bet_info:
            bet_type = bet_info['type']
            bet_amount = bet_info['amount']
            won = False
            payout = 0
            
            if bet_type == 'red' and color == 'red':
                won = True
                payout = bet_amount * 2
            elif bet_type == 'black' and color == 'black':
                won = True
                payout = bet_amount * 2
            elif bet_type == 'green' and color == 'green':
                won = True
                payout = bet_amount * 36
            elif bet_type == 'even' and number > 0 and number % 2 == 0:
                won = True
                payout = bet_amount * 2
            elif bet_type == 'odd' and number > 0 and number % 2 == 1:
                won = True
                payout = bet_amount * 2
            elif bet_type == 'low' and 1 <= number <= 18:
                won = True
                payout = bet_amount * 2
            
            # Adicionar ganho se ganhou
            if won:
                SaldoManager.adicionar_ganho(payout)
        
        roulette_state['result'] = {'number': number, 'color': color}
        roulette_state['spinning'] = False
    
    return jsonify({
        'status': 'finished',
        'result': roulette_state['result']
    })

@casino_bp.route('/status', methods=['GET'])
def roulette_status():
    return jsonify({
        'spinning': roulette_state['spinning'],
        'result': roulette_state['result'],
        'balance': SaldoManager.get_saldo()
    })

# ==================== ENDPOINTS DO BLACKJACK ====================
@casino_bp.route('/blackjack/start', methods=['POST'])
def blackjack_start():
    data = request.json
    bet = data.get('bet', 0)
    success = blackjack_game.start_game(bet)
    
    if success:
        return jsonify({
            'success': True,
            'balance': blackjack_game.balance,
            'player_hand': blackjack_game.player_hand,
            'dealer_hand': [blackjack_game.dealer_hand[0]],
            'player_total': blackjack_game.calculate_hand(blackjack_game.player_hand)
        })
    return jsonify({'success': False})

@casino_bp.route('/blackjack/hit', methods=['POST'])
def blackjack_hit():
    result = blackjack_game.hit()
    if result:
        return jsonify({
            'player_hand': blackjack_game.player_hand,
            'player_total': result['player_total'],
            'busted': result['busted'],
            'balance': blackjack_game.balance
        })
    return jsonify({'error': 'Game not active'})

@casino_bp.route('/blackjack/stand', methods=['POST'])
def blackjack_stand():
    result = blackjack_game.stand()
    if result:
        return jsonify({
            'player_hand': blackjack_game.player_hand,
            'dealer_hand': blackjack_game.dealer_hand,
            'player_total': result['player_total'],
            'dealer_total': result['dealer_total'],
            'won': result['won'],
            'win_amount': result['win_amount'],
            'balance': blackjack_game.balance
        })
    return jsonify({'error': 'Game not active'})

@casino_bp.route('/blackjack/status', methods=['GET'])
def blackjack_status():
    return jsonify({
        'balance': blackjack_game.balance,
        'is_playing': blackjack_game.is_playing
    })

# ==================== ENDPOINTS DO MINES ====================
@casino_bp.route('/mines/start', methods=['POST'])
def mines_start():
    data = request.json
    bet = data.get('bet', 0)
    mines = data.get('mines', 3)
    success = mines_game.start_game(bet, mines)
    return jsonify({'success': success, 'balance': mines_game.balance})

@casino_bp.route('/mines/reveal', methods=['POST'])
def mines_reveal():
    data = request.json
    position = data.get('position', 0)
    result = mines_game.reveal_tile(position)
    result['balance'] = mines_game.balance
    return jsonify(result)

@casino_bp.route('/mines/cashout', methods=['POST'])
def mines_cashout():
    win_amount = mines_game.cashout()
    return jsonify({'winAmount': win_amount, 'balance': mines_game.balance, 'board': mines_game.board})

@casino_bp.route('/mines/status', methods=['GET'])
def mines_status():
    return jsonify({
        'balance': mines_game.balance,
        'multiplier': mines_game.multiplier,
        'isPlaying': mines_game.is_playing
    })

# ==================== ENDPOINTS DO PENALTY ====================
@casino_bp.route('/penalty/shoot', methods=['POST'])
def penalty_shoot():
    data = request.json
    bet = data.get('bet', 0)
    position = data.get('position', 0)
    result = penalty_game.shoot(bet, position)
    return jsonify(result)

@casino_bp.route('/penalty/status', methods=['GET'])
def penalty_status():
    return jsonify({'balance': penalty_game.balance})

# ==================== ENDPOINTS DO RACE ====================
@casino_bp.route('/race/start', methods=['POST'])
def race_start():
    data = request.json
    bet = data.get('bet', 0)
    horse = data.get('horse', 0)
    success = race_game.start_race(bet, horse)
    return jsonify({'success': success, 'balance': race_game.balance})

@casino_bp.route('/race/update', methods=['GET'])
def race_update():
    result = race_game.update_race()
    return jsonify(result)

@casino_bp.route('/race/status', methods=['GET'])
def race_status():
    return jsonify({
        'balance': race_game.balance,
        'isRacing': race_game.is_racing
    })

# ==================== ENDPOINTS DO AVIATOR ====================
@casino_bp.route('/aviator/start', methods=['POST'])
def aviator_start():
    data = request.json
    bet = data.get('bet', 0)
    success = aviator_game.start_flight(bet)
    return jsonify({'success': success, 'balance': aviator_game.balance})

@casino_bp.route('/aviator/status', methods=['GET'])
def aviator_status():
    status = aviator_game.get_status()
    status['balance'] = aviator_game.balance
    return jsonify(status)

@casino_bp.route('/aviator/cashout', methods=['POST'])
def aviator_cashout():
    win_amount = aviator_game.cashout()
    return jsonify({'winAmount': win_amount, 'balance': aviator_game.balance})

# ==================== ENDPOINTS DO DICE ====================
@casino_bp.route('/dice/roll', methods=['POST'])
def dice_roll():
    data = request.json
    bet = data.get('bet', 0)
    bet_type = data.get('betType', '')
    result = dice_game.roll_dice(bet, bet_type)
    return jsonify(result)

@casino_bp.route('/dice/status', methods=['GET'])
def dice_status():
    return jsonify({'balance': dice_game.balance})

# ==================== ENDPOINTS DO SLOTS ====================
@casino_bp.route('/slots/spin', methods=['POST'])
def slots_spin():
    data = request.json
    bet = data.get('bet', 0)
    result = slots_game.spin(bet)
    return jsonify(result)

@casino_bp.route('/slots/status', methods=['GET'])
def slots_status():
    return jsonify({'balance': slots_game.balance})