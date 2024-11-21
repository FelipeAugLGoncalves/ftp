import os
from flask import Flask, request, send_from_directory, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from models import db, File

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3'}
app.secret_key = 'secret'

db.init_app(app)

# Verificar se a pasta de uploads existe, se não, cria
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    files = File.query.all()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Salvar informações do arquivo no banco de dados
        new_file = File(filename=filename, file_path=file_path)
        db.session.add(new_file)
        db.session.commit()

        return redirect(url_for('index'))
    return 'Arquivo não permitido!'

@app.route('/download/<int:file_id>')
def download_file(file_id):
    file = File.query.get(file_id)
    if file:
        return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename)
    return 'Arquivo não encontrado!'

@app.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    file = File.query.get(file_id)
    if file:
        db.session.delete(file)
        db.session.commit()
        os.remove(file.file_path)  # Deletar o arquivo fisicamente
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)
