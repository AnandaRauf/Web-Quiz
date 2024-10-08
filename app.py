from flask import Flask, render_template, request, redirect, url_for, session
from pony.orm import db_session, select
from models import db, Admin, User, Question, Answer

import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Inisialisasi database
db.bind(provider='mysql', host='localhost', user='root', passwd='', db='quiz_db')
db.generate_mapping(create_tables=True)

@app.route('/admin/dashboard', methods=['GET', 'POST'])
@db_session
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    admin = Admin.get(id=session['admin_id'])  # Ambil data admin
    
    if request.method == 'POST':
        question_text = request.form['question']
        Question(text=question_text)
        return redirect(url_for('admin_dashboard'))
    
    questions = select(q for q in Question)[:]
    return render_template('admin_dashboard.html', admin=admin, questions=questions)
	
@app.route('/user/dashboard', methods=['GET'])
@db_session
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Ambil informasi user yang sedang login
    user = User.get(id=session['user_id'])
    
    # Tampilkan semua pertanyaan
    questions = select(q for q in Question)[:]
    
    # Render user_dashboard.html dengan data user dan pertanyaan
    return render_template('user_dashboard.html', user=user, questions=questions)




# Rute untuk mengedit pertanyaan
@app.route('/admin/edit/<int:question_id>', methods=['GET', 'POST'])
@db_session
def edit_question(question_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    question = Question.get(id=question_id)
    if request.method == 'POST':
        new_text = request.form['question']
        question.text = new_text
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_question.html', question=question)

# Rute untuk menghapus pertanyaan
@app.route('/admin/delete/<int:question_id>', methods=['POST'])
@db_session
def delete_question(question_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    question = Question.get(id=question_id)
    question.delete()
    return redirect(url_for('admin_dashboard'))

# Halaman register user
@app.route('/register', methods=['GET', 'POST'])
@db_session
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        if role == 'admin':
            Admin(name=name, email=email, password=password)
        else:
            User(name=name, email=email, password=password, points=0)
        return redirect(url_for('login'))
    return render_template('register_user.html')

@app.route('/login', methods=['GET', 'POST'])
@db_session
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = Admin.get(email=email, password=password)
        user = User.get(email=email, password=password)
        if admin:
            session['admin_id'] = admin.id
            return redirect(url_for('admin_dashboard'))
        elif user:
            session['user_id'] = user.id
            return redirect(url_for('user_dashboard'))
    return render_template('login.html')
	
# Rute untuk logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('admin_id', None)  # Logout admin
    session.pop('user_id', None)  # Logout user (jika ada)
    return redirect(url_for('login'))
	
# Rute untuk menangani form submit di user_dashboard
@app.route('/submit_answer', methods=['POST'])
@db_session
def submit_answer():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    question_id = request.form['question_id']
    answer_text = request.form['answer']

    # Simpan jawaban ke database
    question = Question.get(id=question_id)
    user = User.get(id=session['user_id'])
    Answer(user=user, question=question, text=answer_text)

    return redirect(url_for('thank_you'))

# Rute halaman terima kasih setelah menjawab
@app.route('/thank_you', methods=['GET'])
def thank_you():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('thank_you.html')
if __name__ == '__main__':
    app.run(debug=True)
