from flask import request, make_response, redirect, render_template, session, url_for, flash
from flask_login import login_required, current_user
import unittest
from app import create_app
from app.forms import ToDoForm, DeleteToDoForm, UpdateToDoForm
from app.firestore_service import get_users, get_todos, set_todo, delete_todo, update_todo

app = create_app()

# Nomás para mostrar al principio los datos del lado frontend.
# todos = ['Comprar café', 'Enviar solicitud de compra', 'Entregar video a productor']

# Para generar comandos del command line (command line interface).
@app.cli.command()
def test():
    # Explorar todos los tests encontrados en la carpeta 'tests'.
    tests = unittest.TestLoader().discover('tests')
    # Correr todos los tests.
    unittest.TextTestRunner().run(tests)

# Función decoradora para manejar errores.
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error)

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html', error=error)

@app.route('/')
def index():
    # raise(Exception('500 error'))
    # Se obtiene la IP del usuario.
    user_ip = request.remote_addr
    # Se redirige a la página 'hello' (hello.html).
    response = make_response(redirect('/hello'))
    # Originalmente, se obtiene de las cookies la IP del usuario
    # response.set_cookie('user_ip' , user_ip)
    session['user_ip'] = user_ip
    return response

@app.route('/hello', methods=['GET', 'POST'])
@login_required
def hello():
    # La variable local user_ip obtiene la IP del usuario.
    # user_ip = request.cookies.get('user_ip')
    user_ip = session.get('user_ip')
    # Se guarda suavemente el nombre del usuario.
    # username = session.get('username')
    username = current_user.id

    todo_form = ToDoForm()
    delete_form = DeleteToDoForm()
    update_form = UpdateToDoForm()

    # Con el diccionario 'context' se pasan las variables al template hello.html y ahí
    # ya se pueden manejar como variables locales.
    context = {
        'user_ip': user_ip,
        'todos': get_todos(user_id=username),
        'username': username,
        'todo_form': todo_form,
        'delete_form': delete_form,
        'update_form': update_form
    }

    if todo_form.validate_on_submit():
        set_todo(user_id=username, description=todo_form.description.data)

        flash('Tarea agregada!')

        return redirect(url_for('hello'))

    users = get_users()

    for user in users:
        print(user.id)
        print(user.to_dict()['password'])

    return render_template('hello.html', **context)

@app.route('/todos/delete/<todo_id>', methods=['POST'])
def delete(todo_id):
    user_id = current_user.id
    delete_todo(user_id=user_id, todo_id=todo_id)

    return redirect(url_for('hello'))

@app.route('/todos/update/<todo_id>/<int:done>', methods=['POST'])
def update(todo_id, done):
    user_id = current_user.id
    update_todo(user_id=user_id, todo_id=todo_id, done=done)

    return redirect(url_for('hello'))
