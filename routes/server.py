from flask import Flask, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from all_routes import casino_bp

app = Flask(__name__)

# Configurar CORS mais permissivo
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Inicializar banco
def init_db():
    conn = sqlite3.connect('../casino.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            saldo REAL DEFAULT 1000.0,
            total_ganho REAL DEFAULT 0.0,
            total_perdido REAL DEFAULT 0.0,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE id = 1')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO usuarios (nome, email, senha, saldo) VALUES (?, ?, ?, ?)', 
                      ('Admin', 'admin@casino.com', '123456', 1000000000.0))
    conn.commit()
    conn.close()

init_db()

# Registrar blueprint
app.register_blueprint(casino_bp)

# Servir arquivos HTML da pasta pai
@app.route('/')
def index():
    return send_from_directory('..', 'index.html')

@app.route('/<path:filename>')
def serve_files(filename):
    return send_from_directory('..', filename)

if __name__ == '__main__':
    print("Casino Server - Estrutura Organizada")
    print("HTML: Nova-pasta/")
    print("APIs: Nova-pasta/routes/")
    print("Servidor: http://localhost:8080")
    app.run(debug=True, port=8080, host='0.0.0.0')