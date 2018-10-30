from flask import Flask, request, render_template, flash, abort, url_for, redirect, session, make_response

from flask_sqlalchemy import SQLAlchemy

import datetime

app = Flask(__name__)


class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/blog_1026"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


app.config.from_object(Config)

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(24))
    cat = db.relationship("Category", backref="us")

    def __repr__(self):
        return "user = %s" % self.username


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=True)
    content = db.Column(db.String(100))
    catetime = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


@app.route('/')
def show_entries():
    if session.get("log_out") is True:
        categorys = Category.query.all()
        return render_template('show_entries.html', entries=categorys)
    if request.cookies.get('user'):
        username = request.cookies.get('user')
        if username is not None:
            us1 = User.query.filter_by(username=username).first()
            session["username"] = username
            session["id"] = us1.id
            session['logged_in'] = True
            session["log_out"] = False
    categorys = Category.query.all()
    return render_template('show_entries.html', entries=categorys)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    title = request.form.get("title")
    content = request.form.get("text")
    if not title or not content:
        flash("没有数据添加")
        return redirect(url_for('show_entries'))
    else:
        lll = Category()
        lll.title = title
        lll.content = content
        lll.user_id = session.get("id")
        time = datetime.datetime.now()
        lll.catetime = str(time.year) + "-" + str(time.month) + "-" + str(time.day) \
                       + "  " + str(time.hour) + ":" + str(time.minute)
        db.session.add(lll)
        db.session.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        password = request.form['password']
        if user is None:
            error = '请输入正确的用户名'
        elif password is None:
            error = '请输入密码'
        elif user.password == password:
            session['logged_in'] = True
            session["username"] = request.form['username']
            session["id"] = user.id
            flash('You were logged in')
            resp = make_response(show_entries())
            resp.set_cookie("user", user.username, 36000)
            return resp
        else:
            error = "账号或者密码不对"

    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).all():
            return render_template('register.html', error=error)
        if username is None:
            error = 'Invalid username'
        if password is None:
            error = 'Invalid password'
        else:
            us = User()
            us.username = username
            us.password = password
            db.session.add(us)
            db.session.commit()
            redirect(url_for('show_entries'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session["log_out"] = True
    flash('You were logged out')
    resp = make_response(show_entries())
    resp.delete_cookie("user", "")
    return resp


if __name__ == '__main__':
    app.run()
