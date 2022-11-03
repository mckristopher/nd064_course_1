import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, make_response, session
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# set logger to handle STDOUT and STDERR 
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stderr_handler =  logging.StreamHandler()
stderr_handler.setLevel(logging.WARNING)
handlers = [stderr_handler, stdout_handler]
# format output
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(format)

logging.basicConfig(format=format, level=logging.DEBUG, handlers=handlers)

def update_conxn_count():
    if (session.get('connect_count')):
        session['connect_count'] += 1
    else:
        session['connect_count'] = 1

# Define Health page
@app.route('/healthz')
def health():
    return make_response(
        jsonify({ 'result': 'OK - healthy' }), 200)

#Define Metrics page
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    update_conxn_count()
    posts = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    return make_response(jsonify({
            'db_connection_count': session.get('connect_count'),
            'post_count': posts[0]
        }), 200)

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    update_conxn_count()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    update_conxn_count()
    if post is None:
        app.logger.info('Attempt to Access Invalid Article: %s', post_id)
        return render_template('404.html'), 404
    else:
        app.logger.info('Article %s retrieved',post['title'])
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page viewed')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            update_conxn_count()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info('New Article Created : %s', request.form['title'])
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
