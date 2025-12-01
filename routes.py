from flask import Flask, render_template, session, redirect, url_for, flash, request, send_from_directory, abort, jsonify
import run, queries, report, os

app = Flask(__name__, template_folder='templates', static_folder='static')

app.secret_key = 'relatorio_alunos_secret_key'

@app.route('/')
def index():
    session['indice'] = 0
    session['avaliacoes'] = []
    return render_template('index.html')

@app.route('/alunos/<sala>')
def mostrar_alunos(sala):
    session['sala'] = sala
    alunos = queries.carregar_alunos(sala)
    session['alunos'] = alunos

    if not alunos:
        return f"Nenhum aluno encontrado para a '{sala}'", 404

    indice = session['indice']
    aluno = alunos[indice]
    quantidade_alunos = len(alunos)
       
    avaliacoes = session.get('avaliacoes', [])
    nomes_avaliados = [a['nome'] for a in avaliacoes]
    ids_avaliados = [a['id'] for a in avaliacoes]
    avaliacao_existente = next((a for a in avaliacoes if a['nome'] == aluno['nome']), None)
    
    periodo = queries.periodo(aluno['nome'])

    return render_template(
        'students.html',
        aluno=aluno,
        alunos=alunos,
        quantidade_alunos=quantidade_alunos,
        indice=indice,
        sala=sala,
        avaliacoes=avaliacoes,
        nomes_avaliados=nomes_avaliados,
        avaliacao_existente=avaliacao_existente,
        ids_avaliados=ids_avaliados,
        periodo=periodo,
    )

@app.route('/enviar', methods=['POST'])
def enviar():
    sala = session.get('sala')

    aluno_atual = session['alunos'][session['indice']]
    nota = request.form.get('nota')
    observacao = request.form.get('observacao', '').strip()
    poucotempo = request.form.get('poucotempo')

    if 'avaliacoes' not in session:
        session['avaliacoes'] = []

    session['indice'] += 1
    quantidade_alunos = len(session['alunos'])

    if session['indice'] >= quantidade_alunos:
        if poucotempo == None and nota == None or observacao == '':
            flash("⚠️ Por favor, preencha a nota e a observação antes de continuar.", "erro")
            session['indice'] -= 1
            return redirect(url_for('mostrar_alunos', sala=sala))
        else:
            avaliacoes = session['avaliacoes']
            avaliacoes.append({
                'id': aluno_atual['id'],
                'nome': aluno_atual['nome'],
                'nota': nota,
                'observacao': observacao
            })
            session['avaliacoes'] = avaliacoes

            caminho = report.gerar_relatorio_docx(sala, avaliacoes)
            nome_arquivo = os.path.basename(caminho)
            return redirect(url_for('abrir_relatorio', nome_arquivo=nome_arquivo))

    if poucotempo == None and nota == None or observacao == '':
        flash("⚠️ Por favor, preencha a nota e a observação antes de continuar.", "erro")
        session['indice'] -= 1
        return redirect(url_for('mostrar_alunos', sala=sala))
    else:
        avaliacoes = session['avaliacoes']
        avaliacao_existente = next((a for a in avaliacoes if a['nome'] == aluno_atual['nome']), None)

        if avaliacao_existente:
            avaliacao_existente['nota'] = nota
            avaliacao_existente['observacao'] = observacao
        else:
            avaliacoes.append({
                'id': aluno_atual['id'],
                'nome': aluno_atual['nome'],
                'nota': nota,
                'observacao': observacao
            })

        session['avaliacoes'] = avaliacoes

        return redirect(url_for('mostrar_alunos', sala=sala))
    
@app.route('/abrir_relatorio/<nome_arquivo>')
def abrir_relatorio(nome_arquivo):
    pasta = os.path.join(os.getcwd(), 'relatorios')
    caminho = os.path.join(pasta, nome_arquivo)

    if not os.path.exists(caminho):
        flash("⚠️ Relatório não encontrado.", "erro")
        return redirect(url_for('index'))

    session['ultimo_relatorio'] = nome_arquivo
    flash(f"✅ {nome_arquivo} gerado com sucesso!", "sucesso")

    return redirect(url_for('index'))

@app.route('/download_relatorio/<path:nome_arquivo>')
def download_relatorio(nome_arquivo):
    pasta = os.path.join(os.getcwd(), 'relatorios')
    caminho = os.path.join(pasta, nome_arquivo)

    if not os.path.exists(caminho):
        flash("⚠️ Relatório não encontrado.", "erro")
        return redirect(url_for('index'))

    return send_from_directory(pasta, nome_arquivo, as_attachment=False)

@app.route('/limpar_ultimo_relatorio', methods=['POST'])
def limpar_ultimo_relatorio():
    session.pop('ultimo_relatorio', None)
    return ('', 204)

@app.route('/anterior')
def anterior():
    sala = session.get('sala')
    if 'indice' in session and session['indice'] > 0:
        session['indice'] -= 1
    return redirect(url_for('mostrar_alunos', sala=sala))

@app.route('/ir_para_aluno/<int:indice>')
def ir_para_aluno(indice):
    sala = session.get('sala')
    alunos = session.get('alunos')

    if not alunos or indice < 0 or indice >= len(alunos):
        flash("⚠️ aluno inválido.", "erro")
        return redirect(url_for('mostrar_alunos', sala=sala))

    session['indice'] = indice
    return redirect(url_for('mostrar_alunos', sala=sala))

@app.route('/buscar_sala')
def buscar_sala():
    termo = request.args.get('termo', '').lower().strip()
    resultados = []

    for chave, nome in run.sala_map.items():
        if termo in nome.lower():
            resultados.append({'chave': chave, 'nome': nome})

    return jsonify(resultados)