from flask import Flask, render_template, redirect, url_for, request
        movie_to_update.rating = request.form['rating']
        movie_to_update.review = request.form['review']
        db.session.commit()
        return redirect(url_for('home'))
    movie_id = request.args.get('id') if id is None else id
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
        return redirect(url_for('update', id=j+1))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
