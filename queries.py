import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def carregar_alunos(sala):
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("""
    SELECT DISTINCT id, nome
    FROM alunos 
    WHERE status = ? ORDER BY nome ASC;""", (sala,))

    dados = cursor.fetchall()
    
    cursor.close()
    conexao.close()

    return [{'id': id, 'nome': nome.strip()} for id, nome in dados]

def periodo(aluno):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT t.diasemana, t.periodo
    FROM alunos a
    JOIN turma_aluno ta ON ta.id_aluno = a.id
    JOIN turma t ON t.id_turma = ta.id_turma
    WHERE a.nome = ?
""", (aluno,))
    
    periodo = cursor.fetchone()
        
    conexao.close()
    print(periodo[0] + " - " + periodo[1])
    
    return periodo[0] + " - " + periodo[1]