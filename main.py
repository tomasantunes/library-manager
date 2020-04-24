from flask import Flask, render_template, request, flash, jsonify, session, redirect, Markup
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import datetime
from werkzeug.utils import secure_filename
import os

def connect_db():
	return sqlite3.connect("library.db")

db = connect_db()
LOGIN = False
UPLOAD_FOLDER = '/home/user1/Documents/library-manager/upload'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = "default_key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	print(request.method)
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']

		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	return "OK"



def init():
	db = connect_db()
	c = db.cursor()

	sql_books_table = """ CREATE TABLE IF NOT EXISTS books (
							id integer PRIMARY KEY AUTOINCREMENT,
							isbn text,
							title text,
							content text,
							author text,
							date date
						); """

	c.execute(sql_books_table)

@app.route("/")
def home():
	db = connect_db()
	c = db.execute('SELECT * FROM books')
	rows = c.fetchall()
	books = []

	for row in rows:
		book = {
			'id': row[0],
			'isbn': row[1],
			'title': row[2],
			'content' : Markup(row[3]),
			'author' : Markup(row[4]),
			'date' : datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'),
		}
		books.append(book)

	return render_template("home.html", books=books)

	
@app.route("/add-book", methods=['POST'])
def add_post():
	title = request.form.get('title', "")
	author = request.form.get('author', "")
	content = request.form.get('content', "")

	date = datetime.datetime.now()

	if (title != "" and content != ""):
		db = connect_db()
		db.execute('INSERT INTO books (title, content, author, date) VALUES (?, ?, ?, ?)', [title, content, author, date])
		db.commit()
		return redirect("/")
	return redirect("/")

@app.route("/book/<id>")
def book(id):
	return render_template("book.html", book=id)

if __name__ == "__main__":
	init()
	app.run()