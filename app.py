from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Show, Comment, Like
from forms import RegistrationForm, LoginForm, CommentForm
from flask_login import current_user, logout_user, login_user, login_required, LoginManager
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tvshows.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    response = requests.get('https://api.tvmaze.com/shows')
    shows = response.json()
    formatted_shows = [
        {
            'id': show['id'],
            'name': show['name'],
            'genres': show['genres'],
            'language': show['language'],
            'summary': show.get('summary', 'No summary available'),
            'image_url': show['image']['medium'] if show.get('image') else None,
            'liked': Like.query.filter_by(user_id=current_user.id, show_id=show['id']).first() is not None if current_user.is_authenticated else False,
            'comments': Comment.query.filter_by(show_id=show['id']).all()
        }
        for show in shows
    ]
    return render_template('index.html', shows=formatted_shows)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data
        user = User.register(name, pwd)
        db.session.add(user)
        db.session.commit()
        login_user(user)  # Log in the user after successful registration
        return redirect(url_for('fetch_shows'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():

    logout_user()
    flash("Goodbye!")
    return redirect('/')

@app.route('/secret')
@login_required
def secret():
    liked_show_ids = [like.show_id for like in Like.query.filter_by(user_id=current_user.id).all()]
    liked_shows = []

    for show_id in liked_show_ids:
        response = requests.get(f'https://api.tvmaze.com/shows/{show_id}')
        if response.status_code == 200:
            show_data = response.json()
            liked_shows.append({
                'id': show_data['id'],
                'name': show_data['name'],
                'genres': show_data['genres'],
                'summary': show_data.get('summary', 'No summary available'),
                'image_url': show_data['image']['medium'] if show_data.get('image') else None
            })

    return render_template('secret.html', shows=liked_shows)



@app.route('/shows', methods=['GET'])
def fetch_shows():
    response = requests.get('https://api.tvmaze.com/shows')
    shows = response.json()
    formatted_shows = [
        {
            'id': show['id'],
            'name': show['name'],
            'genres': show['genres'],
            'language': show['language'],
            'summary': show.get('summary', 'No summary available'),
            'image_url': show['image']['medium'] if show.get('image') else None,
            'liked': Like.query.filter_by(user_id=current_user.id, show_id=show['id']).first() is not None if current_user.is_authenticated else False,
            'comments': Comment.query.filter_by(show_id=show['id']).all()
        }
        for show in shows
    ]
    return render_template('shows.html', shows=formatted_shows)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')
        response = requests.get(f'https://api.tvmaze.com/search/shows?q={query}')
        shows = response.json()
        formatted_shows = [
            {
                'id': show['show']['id'],
                'name': show['show']['name'],
                'genres': show['show']['genres'],
                'language': show['show']['language'],
                'summary': show['show'].get('summary', 'No summary available'),
                'image_url': show['show']['image']['medium'] if show['show'].get('image') else None,
                'liked': Like.query.filter_by(user_id=current_user.id, show_id=show['show']['id']).first() is not None if current_user.is_authenticated else False,
                'comments': Comment.query.filter_by(show_id=show['show']['id']).all()
            }
            for show in shows
        ]
        return render_template('search_results.html', shows=formatted_shows)
    return render_template('index.html')

@app.route('/add_comment/<int:show_id>', methods=['POST'])
@login_required
def add_comment(show_id):
    content = request.form.get('content')
    if content:
        comment = Comment(content=content, user_id=current_user.id, show_id=show_id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
    return redirect(url_for('show_detail', show_id=show_id))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        flash('You do not have permission to delete this comment', 'danger')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Your comment has been deleted!', 'success')
    return redirect(url_for('search'))

@app.route('/show/<int:show_id>', methods=['GET', 'POST'])
def show_detail(show_id):
    form = CommentForm()
    show = Show.query.get_or_404(show_id)
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, user_id=current_user.id, show_id=show.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('show_detail', show_id=show.id))
    comments = Comment.query.filter_by(show_id=show_id).all()
    liked = Like.query.filter_by(user_id=current_user.id, show_id=show_id).first() is not None if current_user.is_authenticated else False
    return render_template('show_detail.html', show=show, comments=comments, form=form, liked=liked)

@app.route('/favorite/<int:show_id>', methods=['POST'])
@login_required
def favorite_show(show_id):
    like = Like.query.filter_by(user_id=current_user.id, show_id=show_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        flash('Removed from favorites', 'info')
    else:
        like = Like(user_id=current_user.id, show_id=show_id)
        db.session.add(like)
        db.session.commit()
        flash('Added to favorites', 'success')
    return redirect(request.referrer)

@app.route('/list_shows')
def list_shows():
    shows = Show.query.all()
    return "\n".join([f"Show ID: {show.id}, Show Name: {show.name}" for show in shows])

@app.route('/debug_shows')
def debug_shows():
    response = requests.get('https://api.tvmaze.com/shows')
    shows = response.json()
    return jsonify(shows)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)



