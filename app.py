from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import os

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class MaterialForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    image = FileField('Изображение', validators=[DataRequired()])
    category = StringField('Категория', validators=[DataRequired()])


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash("Неверный логин или пароль")
    return render_template("login.html")


@app.route("/admin")
@login_required
def admin_dashboard():
    materials = Material.query.all()
    return render_template('admin_dashboard.html', materials=materials)


@app.route("/admin/add", methods=["GET", "POST"])
@login_required
def add_material():
    form = MaterialForm()
    if form.validate_on_submit():
        filename = os.path.join(app.config['UPLOAD_FOLDER'], form.image.data.filename)
        form.image.data.save(filename)
        new_material = Material(
            title=form.title.data,
            content=form.content.data,
            image=form.image.data.filename,
            category=form.category.data
        )
        db.session.add(new_material)
        db.session.commit()
        flash('Материал добавлен!')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_material.html', form=form)


@app.route("/home")
def home():
    materials = Material.query.filter_by(category='Главная').all()
    return render_template("content_page.html", title="Главная", materials=materials)


@app.route("/about")
def about():
    materials = Material.query.filter_by(category='О клубе').all()
    return render_template("content_page.html", title="О клубе", materials=materials)


@app.route("/news")
def news():
    materials = Material.query.filter_by(category='Новости').all()
    return render_template("content_page.html", title="Новости", materials=materials)


@app.route("/resources")
def resources():
    materials = Material.query.filter_by(category='Полезные материалы').all()
    return render_template("content_page.html", title="Полезные материалы", materials=materials)


@app.route("/gallery")
def gallery():
    materials = Material.query.filter_by(category='Галерея').all()
    return render_template("content_page.html", title="Галерея", materials=materials)


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == '__main__':
    # Открываем контекст приложения для работы с базой данных
    with app.app_context():
        db.create_all()  # Создаем таблицы
    app.run(app.run(ssl_context=('cert.pem', 'key.pem')))
