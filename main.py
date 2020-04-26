from flask import Flask, render_template, request, flash, jsonify, session, redirect, Markup
import sqlite3
import datetime
import os

def connect_db():
	return sqlite3.connect("library.db")

db = connect_db()

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = "default_key"

def init():
	db = connect_db()
	c = db.cursor()

	sql_books_table = """ CREATE TABLE IF NOT EXISTS books (
							id integer PRIMARY KEY,
							title text,
							description text,
							content text,
							author text,
							date text
						); """

	c.execute(sql_books_table)

def getBooksList():
	db = connect_db()
	c = db.execute('SELECT * FROM books')
	rows = c.fetchall()
	books = []

	for row in rows:
		book = {
			'id': row[0],
			'title': row[1],
			'description' : Markup(row[2]),
			'content' : Markup(row[3]),
			'author' : row[4],
			'date' : datetime.datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'),
			
		}

		books.append(book)
	
	return books

def getBookById(id):
	db = connect_db()
	c = db.execute('SELECT * FROM books WHERE id = ?', [id])
	rows = c.fetchall()
	b = rows[0]

	book = {
		'id':b[0],
		'title': b[1],
		'description' : Markup(b[2]),
		'content' : Markup(b[3]),
		'author' : b[4],
		'date' : datetime.datetime.strptime(b[5], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'),
	}

	return book

@app.route("/")
def books():
	books = getBooksList()
	return render_template("books.html", books=books)

@app.route("/get-books", methods=['GET'])
def getBooks():
	books = getBooksList()
	return jsonify(books)

@app.route("/new-book")
def newBook():
	return render_template("new-book.html")

@app.route("/edit-book/<book>")
def editBookById(book):
	books = getBooksList()
	return render_template("edit-book.html", book=book, books=books)

@app.route("/get-book", methods=['GET'])
def getBookByIdRoute():
	id = request.args.get('id', "")
	book = getBookById(id)
	return jsonify(book)

@app.route("/new-chapter/<book>")
def newChapter(book):
	return render_template("new-chapter.html", book=book)
		
@app.route("/add-book", methods=['POST'])
def addBook():
	title = request.form.get('title', "")
	author = request.form.get('author', "")
	description = request.form.get('description', "")
	content = request.form.get('content', "")

	date = datetime.datetime.now()

	if (title != "" and author != "" and description != ""):
		db = connect_db()
		db.execute('INSERT INTO books (title, author, description, content, date) VALUES (?, ?, ?, ?, ?)', [title, author, description, content, date])
		db.commit()
		return redirect("/")
	else:
		return "Submission Invalid"

@app.route("/update-book", methods=['POST'])
def updateBook():
	id = request.form.get('id', "")
	title = request.form.get('title', "")
	author = request.form.get('author', "")
	description = request.form.get('description', "")
	content = request.form.get('content', "")

	date = str(datetime.datetime.now())

	if (title != "" and author != "" and description != ""):
		db = connect_db()
		db.execute('UPDATE books SET title = ?, author = ?, description = ?, content = ?, date = ? WHERE id = ?;', (title, author, description, content, date, id))
		db.commit()
		return redirect("/edit-book/" + id)
	else:
		return "Submission Invalid"

@app.route("/delete-book", methods=['POST'])
def deleteBook():
	id = request.form.get('id', "")

	if (id != ""):
		db = connect_db()
		db.execute('DELETE FROM books WHERE id = ?;', (id,))
		db.commit()
		return redirect("/")
	else:
		return "Submission Invalid"
 
if __name__ == "__main__":
	init()
	app.run()