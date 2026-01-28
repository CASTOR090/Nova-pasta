import sqlite3

def update_all_balances():
    try:
        conn = sqlite3.connect('casino.db')
        cursor = conn.cursor()
        
        # Atualizar saldo de TODOS os usuários para 1 bilhão
        cursor.execute("UPDATE usuarios SET saldo = 1000000000")
        
        # Verificar quantos foram atualizados
        rows_affected = cursor.rowcount
        print(f"Saldo atualizado para R$ 1.000.000.000 de {rows_affected} usuários")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar banco: {e}")

if __name__ == "__main__":
    update_all_balances()
