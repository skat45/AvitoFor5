from flask import render_template, request, redirect, flash
from flask_login import LoginManager, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from app import app
from db_and_models import User, Advertisement, db
from string import ascii_lowercase
from random import choice

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'


UPLOAD_FOLDER = 'templates/static/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    """ Main page """
    name = None
    isAuth = current_user.is_authenticated
    if isAuth:
        name = current_user.login
    advertisements = Advertisement.query.all()[::-1]
    nuber_of_advertisements = len(advertisements)
    return render_template('index.html', isAuth=isAuth, name=name, nuber_of_advertisements=nuber_of_advertisements,
                           advertisements=advertisements)


@app.route('/register_page')
def register_page():
    """ Main page """
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def new_user():
    login = request.form.get("login")
    password = request.form.get("password")
    room = request.form.get("room")
    user_before = User.query.filter_by(login=login).first()
    if user_before:
        flash('Такой логин уже есть ::(')
        return redirect('/register_page')
    User.add(user_login=login, user_password_hash=generate_password_hash(password), user_room=room)
    return redirect('/auth_page')


@app.route('/auth_page')
def auth_page():
    return render_template('auth.html')


@app.route('/auth', methods=['POST'])
def auth():
    login = request.form.get("login")
    password = request.form.get("password")
    user = User.query.filter_by(login=login).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return redirect('/')
    else:
        flash('Введённые данные неверны')
        return redirect('/auth_page')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect('/')


@app.route('/lk')
def lk():
    if not current_user.is_authenticated:
        return redirect('/auth_page')
    name = current_user.login
    room = current_user.room
    vk = current_user.vk
    tg = current_user.tg
    mobile = current_user.mobile
    if vk is None:
        vk = ''
    if tg is None:
        tg = ''
    if mobile is None:
        mobile = ''
    return render_template('lk.html', name=name, room=room, vk=vk, tg=tg, mobile=mobile)


@app.route('/editing', methods=['POST', 'GET'])
def editing():
    if not current_user.is_authenticated:
        return redirect('/auth_page')

    login = request.form.get("login")
    name = login
    room = request.form.get("room")
    vk = request.form.get("vk")
    tg = request.form.get("tg")
    mobile = request.form.get("mobile")
    password = request.form.get("password")
    if not login or not room:
        flash('Имя/логин и комната должны быть указаны!')
    current_user.login = login
    current_user.room = room
    current_user.vk = vk
    current_user.tg = tg
    current_user.mobile = mobile
    if password:
        current_user.password_hash = generate_password_hash(password)
    try:
        db.session.commit()
        flash('Сохранено')
    except:
        flash('Ошибка базы данных')
    return redirect('/lk')


@app.route('/new_advertisement', methods=['POST', 'GET'])
def new_advertisement():
    if not current_user.is_authenticated:
        return redirect('/auth_page')

    if request.method == 'POST':
        file = None
        file_ok = False
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                file = None
        if file:
            if allowed_file(file.filename):
                file_ok = True

        name = request.form.get('name')
        cost_type = request.form['cost_type']
        cost_in_rubles = request.form.get('cost_in_rubles')
        diff_cost = request.form.get('diff_cost')
        description = request.form.get('description')

        cost_ok = (cost_type == 'rub' and cost_in_rubles) or \
                   (cost_type == 'free') or (cost_type == 'diff' and diff_cost)

        if cost_ok and name:
            filename = ''
            if file_ok:
                filename = ''.join(choice(ascii_lowercase) for i in range(30)) + '.' + file.filename.split('.')[-1]
                while Advertisement.query.filter_by(image=filename).first() is not None:
                    filename = ''.join(choice(ascii_lowercase) for i in range(30)) + '.' + file.filename.split('.')[-1]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = 'no_photo.png'

            if cost_type == 'rub':
                cost = cost_in_rubles + '₽'
            elif cost_type == 'free':
                cost = 'Бесплатно'
            else:
                cost = diff_cost

            Advertisement.add(name=name, lacost=cost, desc=description, image_name=filename, o_id=current_user.id)

            flash('Объявление размещено')
        else:
            flash('Проверьте название и указание цены')
        return redirect('/new_advertisement')
    return render_template('new_advertisement.html', name=current_user.login)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/adv/<int:id>', methods=['GET', 'POST'])
def adv(id):
    advertisement = Advertisement.query.filter_by(id=id).first()
    if request.method == 'POST':
        db.session.delete(advertisement)
        db.session.commit()
        return redirect('/')
    is_auth = current_user.is_authenticated
    owner = advertisement.owner_id
    user = User.query.filter_by(id=owner).first()
    vk = user.vk
    tg = user.tg
    mobile = user.mobile
    room = user.room
    name = user.login
    uid = None
    if current_user.is_authenticated:
        uid = current_user.id

    return render_template('adv.html', uid=uid, owner=owner, isAuth=is_auth, adv=advertisement, vk=vk, tg=tg, mobile=mobile, room=room, name=name)


if __name__ == "__main__":
    app.run(debug=True)
