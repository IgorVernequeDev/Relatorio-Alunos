import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

def carregar_alunos(sala):
    conexao = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conexao.cursor()
    
    cursor.execute("""
    SELECT DISTINCT id, nome
    FROM alunos 
    WHERE status = %s ORDER BY nome ASC;""", (sala,))

    dados = cursor.fetchall()
    
    cursor.close()
    conexao.close()

    return [{'id': id, 'nome': nome.strip()} for id, nome in dados]

def periodo(aluno):
    conexao = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT t.diasemana, t.periodo
    FROM alunos a
    JOIN turma_aluno ta ON ta.id_aluno = a.id
    JOIN turma t ON t.id_turma = ta.id_turma
    WHERE a.nome = %s
""", (aluno,))
    
    periodo = cursor.fetchone()
        
    conexao.close()
    print(periodo[0] + " - " + periodo[1])
    
    return periodo[0] + " - " + periodo[1]