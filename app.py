import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import logging
from flask import send_file
from io import BytesIO
from PIL import Image
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

# Инициализация Flask приложения
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://@DESKTOP-VF9RI0P\SQLEXPRESS/FIZORGER-DB?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SECRET_KEY'] = 'dde8a6ba4fdf7dbecb55874b5c03d02fd575d5ad4623e70c'

# Инициализация SQLAlchemy
db = SQLAlchemy(app)

# Проверка подключения к базе данных
try:
    with app.app_context():
        db.session.execute(text("SELECT 1"))
        print("Подключение к базе данных успешно!")
except OperationalError as e:
    print(f"Ошибка подключения к базе данных: {e}")

logging.basicConfig(level=logging.DEBUG)
logging.debug(f"SECRET_KEY настроен: {app.config['SECRET_KEY']}")

# Определение моделей
class User(db.Model):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    roleID = Column(Integer, nullable=False)
    surname = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    patronymic = Column(String(50), nullable=True)
    login = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    genderID = Column(Integer, ForeignKey('Gender.id'), nullable=True)
    groupID = Column(Integer, ForeignKey('Group.id'), nullable=True)
    image = Column(LargeBinary, nullable=True)

    gender = relationship('Gender', back_populates='users')
    group = relationship('Group', back_populates='users')

class Gender(db.Model):
    __tablename__ = 'Gender'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    users = relationship('User', back_populates='gender')

class Group(db.Model):
    __tablename__ = 'Group'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    users = relationship('User', back_populates='group')

class News(db.Model):
    __tablename__ = 'News'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    imageURL = Column(String(255), nullable=True)
    date = Column(Date, nullable=False)

class Command(db.Model):
    __tablename__ = 'Command'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

class Event(db.Model):
    __tablename__ = 'Event'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sportTypeID = Column(Integer, nullable=False)

class MediaCards(db.Model):
    __tablename__ = 'MediaCards'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    mediaType = Column(String(50), nullable=False)
    mediaUrl = Column(String(255), nullable=False)

class ScheduleSections(db.Model):
    __tablename__ = 'ScheduleSections'
    id = Column(Integer, primary_key=True)
    sportTypeID = Column(Integer, nullable=False)
    time = Column(String(11), nullable=False)
    date = Column(Date, nullable=False)

class StudentInCommand(db.Model):
    __tablename__ = 'StudentInCommand'
    id = Column(Integer, primary_key=True)
    studID = Column(Integer, ForeignKey('User.id'), nullable=False)
    groupID = Column(Integer, ForeignKey('Group.id'), nullable=False)
    commandID = Column(Integer, ForeignKey('Command.id'), nullable=False)
    date = Column(Date, nullable=False)

class Award(db.Model):
    __tablename__ = 'Award'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    recipient = Column(String(255), nullable=False)
    image = Column(String(255), nullable=True)

def update_user_password(login, plain_password):
    with app.app_context():
        hashed_password = generate_password_hash(plain_password, method='pbkdf2:sha256')
        user = db.session.execute(db.select(User).filter_by(login=login)).scalar_one_or_none()
        if user:
            user.password = hashed_password
            db.session.commit()
            logging.debug(f"Пароль обновлен для пользователя {user.login}")
        else:
            logging.debug("Пользователь не найден")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/media')
def media():
    return render_template('media.html')

@app.route('/media_video')
def media_video():
    return render_template('media_video.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/measure')
def measure():
    return render_template('measure.html')

@app.route('/measure_upcoming')
def measure_upcoming():
    return render_template('measure_upcoming.html')

@app.route('/measure_past')
def measure_past():
    return render_template('measure_past.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/user_panel')
def user_panel():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user and user.roleID == 1:  # Администратор
            return render_template('user_panel.html', user=user)
    return redirect(url_for('login'))

@app.route('/physorg_panel')
def physorg_panel():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user and user.roleID == 2:  # Физорг
            return render_template('physorg_panel.html', user=user)
    return redirect(url_for('login'))

@app.route('/api/user_data', methods=['GET'])
def get_user_data_route():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            user_data = {
                'surname': user.surname,
                'name': user.name,
                'patronymic': user.patronymic,
                'login': user.login,
                'gender': user.genderID,
                'group': user.groupID,
                'role': user.roleID  # Добавьте поле роли
            }
            return jsonify(user_data)
    return jsonify({'error': 'Пользователь не найден'}), 404

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_login = request.form['login']
        user_password = request.form['password']
        user = db.session.execute(db.select(User).filter_by(login=user_login)).scalar_one_or_none()
        if user and check_password_hash(user.password, user_password):
            session['user_id'] = user.id
            if user.roleID == 1:  # Администратор
                return redirect(url_for('user_panel'))
            elif user.roleID == 2:  # Физорг
                return redirect(url_for('physorg_panel'))
            else:
                flash('Неверная роль пользователя', 'error')
                return redirect(url_for('login'))
        else:
            flash('Неверный логин или пароль', 'error')
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user_login = data.get('login')
    user_password = data.get('password')
    user = db.session.execute(db.select(User).filter_by(login=user_login)).scalar_one_or_none()
    if user:
        if check_password_hash(user.password, user_password):
            session['user_id'] = user.id
            role = 'admin' if user.roleID == 1 else 'physorg'
            return jsonify({
                "success": True,
                "redirect": url_for('user_panel') if user.roleID == 1 else url_for('physorg_panel'),
                "role": role
            }), 200
        else:
            return jsonify({"success": False, "message": "Неверный логин или пароль"}), 401
    else:
        return jsonify({"success": False, "message": "Неверный логин или пароль"}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({"success": True, "message": "Выход выполнен успешно"}), 200

@app.route('/api/add_news', methods=['POST'])
def add_news_route():
    title = request.form['title']
    content = request.form['content']
    image = request.files.get('image')
    date = request.form['date']

    if image:
        img = Image.open(image.stream)
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
    else:
        img_byte_arr = None

    new_news = News(
        title=title,
        content=content,
        imageURL=img_byte_arr,
        date=date
    )
    db.session.add(new_news)
    db.session.commit()

    return jsonify({"success": True, "message": "Новость добавлена успешно"}), 200

@app.route('/api/get_news', methods=['GET'])
def get_news():
    news = News.query.all()
    return jsonify({'news': [{'id': n.id, 'title': n.title, 'content': n.content, 'date': n.date, 'imageURL': n.imageURL} for n in news]})

@app.route('/api/get_news_image/<int:news_id>', methods=['GET'])
def get_news_image(news_id):
    news = db.session.get(News, news_id)
    if news and news.imageURL:
        return send_file(BytesIO(news.imageURL), mimetype='image/jpeg')
    return jsonify({"error": "Изображение не найдено"}), 404

@app.route('/api/add_command', methods=['POST'])
def add_command():
    name = request.form['name']
    new_command = Command(name=name)
    db.session.add(new_command)
    db.session.commit()
    return jsonify({"success": True, "message": "Команда добавлена успешно"}), 200

@app.route('/api/get_commands', methods=['GET'])
def get_commands():
    commands = Command.query.all()
    return jsonify({'commands': [{'id': c.id, 'name': c.name} for c in commands]})

@app.route('/api/add_team', methods=['POST'])
def add_team():
    try:
        command_name = request.form['team_name']
        course_id = request.form['course']
        sport_type_id = request.form['sport_type']
        gender_id = request.form['gender']
        team_members = request.form.getlist('team_members[]')
        reserve_member = request.form['reserve_member']

        # Проверка на существование пользователей в таблице User
        users = db.session.query(User).filter(User.id.in_(team_members + [reserve_member])).all()
        if len(users) != len(team_members) + 1:
            return jsonify({"success": False, "message": "Один или несколько пользователей не найдены"}), 400

        # Создание новой команды
        new_command = Command(name=command_name)
        db.session.add(new_command)
        db.session.commit()

        # Добавление участников команды
        for member in team_members:
            new_member = StudentInCommand(commandID=new_command.id, studID=member, groupID=users[team_members.index(member)].groupID, date=datetime.now().date())
            db.session.add(new_member)

        # Добавление запасного игрока
        new_reserve_member = StudentInCommand(commandID=new_command.id, studID=reserve_member, groupID=users[len(team_members)].groupID, date=datetime.now().date())
        db.session.add(new_reserve_member)

        db.session.commit()

        return jsonify({"success": True, "message": "Команда добавлена успешно"}), 200
    except KeyError as e:
        return jsonify({"success": False, "message": f"Отсутствуют данные формы: {e}"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/add_event', methods=['POST'])
def add_event():
    name = request.form['name']
    date = request.form['date']
    location = request.form['location']
    description = request.form['description']
    sportTypeID = request.form['sportTypeID']
    new_event = Event(name=name, date=date, location=location, description=description, sportTypeID=sportTypeID)
    db.session.add(new_event)
    db.session.commit()
    return jsonify({"success": True, "message": "Мероприятие добавлено успешно"}), 200

@app.route('/api/get_events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify({'events': [{'id': e.id, 'name': e.name, 'date': e.date, 'location': e.location, 'description': e.description, 'sportTypeID': e.sportTypeID} for e in events]})

@app.route('/api/add_media', methods=['POST'])
def add_media():
    title = request.form['title']
    mediaType = request.form['mediaType']
    mediaUrl = request.form['mediaUrl']
    new_media = MediaCards(title=title, mediaType=mediaType, mediaUrl=mediaUrl)
    db.session.add(new_media)
    db.session.commit()
    return jsonify({"success": True, "message": "Медиа добавлено успешно"}), 200

@app.route('/api/get_media', methods=['GET'])
def get_media():
    media = MediaCards.query.all()
    return jsonify({'media': [{'id': m.id, 'title': m.title, 'mediaType': m.mediaType, 'mediaUrl': m.mediaUrl} for m in media]})

@app.route('/api/edit_schedule', methods=['POST'])
def edit_schedule():
    data = request.form
    schedule = ScheduleSections.query.get(data['id'])
    if schedule:
        schedule.time = data['time']
        schedule.date = data['date']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Расписание обновлено успешно'}), 200
    return jsonify({'success': False, 'message': 'Расписание не найдено'}), 404

@app.route('/api/get_schedule', methods=['GET'])
def get_schedule():
    schedule = ScheduleSections.query.all()
    return jsonify({'schedule': [{'id': s.id, 'sportTypeID': s.sportTypeID, 'time': s.time, 'date': s.date} for s in schedule]})

@app.route('/api/add_physorg', methods=['POST'])
def add_physorg():
    surname = request.form['surname']
    name = request.form['name']
    patronymic = request.form['patronymic']
    gender = request.form['gender']
    group = request.form['group']
    login = request.form['login']
    password = request.form['password']

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    gender_id = db.session.query(Gender).filter_by(name=gender).first().id
    group_id = db.session.query(Group).filter_by(name=group).first().id

    new_user = User(
        roleID=2,
        surname=surname,
        name=name,
        patronymic=patronymic,
        login=login,
        password=hashed_password,
        genderID=gender_id,
        groupID=group_id
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True, "message": "Физорг добавлен успешно"}), 200

@app.route('/api/profile_picture', methods=['GET', 'POST'])
def profile_picture():
    user_id = session.get('user_id')
    if request.method == 'GET':
        if user_id:
            user = db.session.get(User, user_id)
            if user.image:
                return send_file(BytesIO(user.image), mimetype='image/jpeg')
            else:
                return send_file('static/style/icon-placeholder.png', mimetype='image/png')
        return jsonify({'error': 'Пользователь не найден'}), 404
    elif request.method == 'POST':
        if user_id:
            if 'profile_picture' not in request.files:
                return jsonify({'error': 'Файл не найден в запросе'}), 400
            file = request.files['profile_picture']
            if file.filename == '':
                return jsonify({'error': 'Не выбран файл'}), 400
            try:
                img = Image.open(file.stream)
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                user = db.session.get(User, user_id)
                user.image = img_byte_arr
                db.session.commit()
                return jsonify({'success': True, 'message': 'Фото профиля обновлено'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        return jsonify({'error': 'Пользователь не найден'}), 404

@app.route('/api/delete_profile_picture', methods=['POST'])
def delete_profile_picture():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        user.image = None
        db.session.commit()
        return jsonify({"success": True, "message": "Фото профиля удалено успешно"}), 200
    return jsonify({"error": "Пользователь не найден"}), 404

@app.route('/api/add_award', methods=['POST'])
def add_award():
    name = request.form['name']
    recipient = request.form['recipient']
    image = request.files.get('image')

    if image:
        img = Image.open(image.stream)
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
    else:
        img_byte_arr = None

    new_award = Award(name=name, recipient=recipient, image=img_byte_arr)
    db.session.add(new_award)
    db.session.commit()

    return jsonify({"success": True, "message": "Награда добавлена успешно"}), 200

if __name__ == '__main__':
    if os.getenv('FLASK_ENV') != 'testing':
        update_user_password('admin', 'admin')
        update_user_password('isp-22p', '12345678')

    app.run(debug=True)
