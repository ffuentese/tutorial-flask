# all the imports
import os
import sqlite3 
from app import app
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash




# Load default config and override config from an environment variable
app.config.from_object(__name__) # load config from this file , flaskr.py
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='devel key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
    


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
    
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()    
        
@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select id, title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)
    
@app.route('/post/<int:postID>')
def show_entry(postID):
    db = get_db()
    cur = db.execute('select id, title, text from entries where id = ?', (postID,))
    entry = cur.fetchone()
    comments = show_comments(postID)
    return render_template('show_post.html', entry=entry, comments=comments)
    
def show_comments(postID):
    db = get_db()
    cur = db.execute('select id, name, text from comments where entry_id = ? order by id desc', (postID,))
    comments = cur.fetchall()
    return comments
    
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))
    
@app.route('/addcomment/<int:entry_id>', methods=['POST'])
def add_comment(entry_id):
    # if not session.get('logged_in'):
    #     abort(401)
    db = get_db()
    db.execute('insert into comments (name, text, entry_id) values (?, ?, ?)',
                 [request.form['name'], request.form['text'], entry_id])
    db.commit()
    flash('New comment was successfully posted')
    return redirect(url_for('show_entry', postID=entry_id))    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)
    
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))    
    

