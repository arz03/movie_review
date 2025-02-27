from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies-collection.db"
db.init_app(app)


# CREATE TABLE
class Movie(db.Model):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(500), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


# with app.app_context():
#     new_movie = Movie(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
    # second_movie = Movie(
    #     id=2,
    #     title="Avatar The Way of Water",
    #     year=2022,
    #     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
    #     rating=7.3,
    #     ranking=9,
    #     review="I liked the water.",
    #     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
    # )
    # db.session.add(new_movie)
    # db.session.commit()


class UpdateForm(FlaskForm):

    rating = FloatField(label='Your Rating out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label='Done', validators=[DataRequired()])


class AddForm(FlaskForm):

    title = StringField(label='Movie Title', validators=[DataRequired()])
    add_movie = SubmitField(label='Add Movie', validators=[DataRequired()])


@app.route("/")
def home():
    with app.app_context():
        result = db.session.execute(db.select(Movie).order_by(Movie.rating))
        db.session.commit()
        all_movies = result.scalars().all()
        for i in range(len(all_movies)):
            all_movies[i].ranking = len(all_movies) - i
        db.session.commit()
        return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=['GET', 'POST'])
def update():
    update_form = UpdateForm()
    if request.method == 'POST':
        movie_id = request.args.get('id')
        movie_to_update = db.get_or_404(Movie, movie_id)
        movie_to_update.rating = request.form['rating']
        movie_to_update.review = request.form['review']
        db.session.commit()
        return redirect(url_for('home'))
    movie_id = request.args.get('id')
    movie_selected = db.get_or_404(Movie, movie_id)
    return render_template("edit.html", form=update_form, movie=movie_selected)


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=['GET', 'POST'])
def add():
    add_form = AddForm()
    if request.method == 'POST':
        movie_title = request.form['title']
        return redirect(url_for('movie_list', movie=movie_title))
    return render_template('add.html', form=add_form)


@app.route("/find", methods=['GET', 'POST'])
def movie_list():
    proton_vpn_pass = "v]:lHCh=wyHY(fT]"
    API_KEY = "3bf919768dd73bca398a61d21adb6c53"
    query = {
        'query': f'{request.args.get("movie")}'
    }
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer 3bf919768dd73bca398a61d21adb6c53"
    }
    response_for_movies = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key=3bf919768dd73bca398a61d21adb6c53&include_adult=false&language=en-US&page=1", params=query)
    response_for_movies.raise_for_status()
    movie_list = response_for_movies.json()

    return render_template('select.html', movie_data=movie_list['results'])


@app.route('/get_details')
def movie_details():
    update_form = UpdateForm()
    movie_id = request.args.get('movie_id')
    print(movie_id)
    response_for_details = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3bf919768dd73bca398a61d21adb6c53&language=en-US" )
    response_for_details.raise_for_status()
    movie_data = response_for_details.json()
    with app.app_context():
        result = db.session.execute(db.select(Movie).order_by(Movie.title))
        all_movies = result.scalars()
        j = 0
        for i in all_movies:
            j += 1
    with app.app_context():
        new_movie = Movie(
            id=j+1,
            title=movie_data['title'],
            img_url=f"https://image.tmdb.org/t/p/w500/{movie_data['poster_path']}",
            year=movie_data['release_date'].split("-")[0],
            description=movie_data['overview'])
        db.session.add(new_movie)
        db.session.commit()
        # movie_selected = db.get_or_404(Movie, movie_id)
        movie_selected = db.get_or_404(Movie, j+1)
        print(movie_selected, update_form)
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
