from flask import Flask, render_template, g, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import sqlite3 
import os 

app = Flask(__name__)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.secret_key = "chave_segura_para_flash"  # Necessário para usar flash

DATABASE = os.path.join(os.path.dirname(__file__), 'bancoTeste.db')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para conectar ao banco de dados
def get_db_connection():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # permite acessar resultados como dicionário
    return conn


# Fecha conexão quando a aplicação termina
@app.teardown_appcontext
def close_connection(exception):
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()


# Rotas básicas
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/cestas-buy")
def cestas_buy():
    return render_template("cestas-buy.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/eclairs-buy")
def eclairs_buy():
    return render_template("eclairs-buy.html")

@app.route("/gateus-buy")
def gateus_buy():
    return render_template("gateus-buy.html")


@app.route("/milfolhas-buy")
def milfolhas_buy():
    return render_template("milfolhas-buy.html")

@app.route("/pagina-compra")
def pagina_compra():
    return render_template("pagina-compra.html")

# CRUD Produtos

#mostra todos os produtos cadastrado no banco de dados
@app.route("/produtos")
def produtos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    return render_template("produtos.html", produtos=produtos)


#pega os dados do formulario a cerca do novo produto e os insere na tabela
@app.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        preco = request.form["preco"]

        file = request.files.get('imagem')
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, imagem) VALUES (?, ?, ?, ?)",
            (nome, descricao, preco, filename)
        )
        conn.commit()
        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for("produtos"))

    return render_template("novo.html")



#exclui o produto do banco de dados atraves de seu id
@app.route('/excluir/<int:id>', methods=['GET', 'POST'])
def excluir(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM produtos WHERE id = ?', (id,))
    conn.commit()
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('produtos'))


#edita produto no bd
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos WHERE id = ?', (id,))
    produto = cursor.fetchone()
    if produto is None:
        flash('Produto não encontrado.', 'error')
        return redirect(url_for('produtos'))

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']

        file = request.files.get('imagem')
        filename = produto['imagem']  # mantém imagem antiga caso não envie nova

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor.execute(
            'UPDATE produtos SET nome = ?, descricao = ?, preco = ?, imagem = ? WHERE id = ?',
            (nome, descricao, preco, filename, id)
        )
        conn.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('produtos'))

    return render_template('editar.html', produto=produto)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM login WHERE email = ? AND senha = ?', (email, senha)).fetchone()
        conn.close()
        
        if user:
            session['usuario'] = user['nome']
            flash(f"Bem-vindo(a), {user['nome']}!", 'success')
            return redirect(url_for('home'))
        else:
            flash('Email ou senha incorretos.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o email já existe
        user_exists = cursor.execute('SELECT * FROM login WHERE email = ?', (email,)).fetchone()
        if user_exists:
            flash('Email já cadastrado!', 'danger')
            return redirect(url_for('register'))

        cursor.execute('INSERT INTO login (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha))
        conn.commit()
        flash('Cadastro realizado com sucesso! Agora faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/editar_conta', methods=['GET', 'POST'])
def editar_conta():
    if 'usuario' not in session:
        flash('Você precisa estar logado para editar sua conta.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Recupera dados atuais do usuário
    user = cursor.execute('SELECT * FROM login WHERE nome = ?', (session['usuario'],)).fetchone()
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        # Verifica se o email é único (exceto o próprio usuário)
        existing_user = cursor.execute('SELECT * FROM login WHERE email = ? AND id != ?', (email, user['id'])).fetchone()
        if existing_user:
            flash('Email já cadastrado por outro usuário.', 'danger')
            return redirect(url_for('editar_conta'))

        cursor.execute('UPDATE login SET nome = ?, email = ?, senha = ? WHERE id = ?',
                       (nome, email, senha, user['id']))
        conn.commit()
        session['usuario'] = nome  # Atualiza nome na sessão
        flash('Conta atualizada com sucesso!', 'success')
        return redirect(url_for('home'))

    return render_template('editar_conta.html', user=user)

@app.route('/excluir_conta', methods=['POST'])
def excluir_conta():
    if 'usuario' not in session:
        flash('Você precisa estar logado para excluir sua conta.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Localiza e exclui o usuário pelo nome atual na sessão
    cursor.execute('DELETE FROM login WHERE nome = ?', (session['usuario'],))
    conn.commit()
    session.pop('usuario', None)
    flash('Conta excluída com sucesso.', 'info')
    return redirect(url_for('home'))



# Inicializa o servidor Flask
if __name__ == "__main__":
    app.run(debug=True)
