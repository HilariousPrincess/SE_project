# -*- coding: utf-8 -*-
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
	 render_template, abort, g, flash, _app_ctx_stack
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#U___
@app.route('/reader_login', methods=['GET', 'POST'])
def reader_login():
	global CURRENT_READER
	error = None
	if request.method == 'POST':
		user = query_db('''select * from users where user_num = ?''',
				[request.form['username']], one=True)
		if user is None:
			error = 'Invalid username'
		elif not check_password_hash(user['pwd'], request.form['password']):
			error = 'Invalid password'
		else:
			session['user_id'] = user['user_name']
			return redirect(url_for('reader'))
	return render_template('reader_login.html', error = error)

# 添加简单的安全性检查
def reader_judge():
	#print(g.user)
	global CURRENT_READER
	CURRENT_READER = g.user
	if not session['user_id']:
		error = 'Invalid reader, please login'
		return render_template('reader_login.html', error = error)

def user_judge():
	if not session['user_id']:
		error = 'Invalid user, please login'
		return render_template('reader_login.html', error = error)

@app.route('/reader')
def reader():
	reader_judge()
	return render_template('reader.html')

#U___
def get_user_id(usernum):
	rv = query_db('select user_id from users where user_name = ?',
				  [usernum], one=True)
	return rv[0] if rv else None

#U___
@app.route('/reader/info', methods=['GET', 'POST'])
def reader_info():
	global CURRENT_READER
	reader_judge()
	user = query_db('''select * from users where user_num=? ''', [g.user], one = True)
	print(user)
	return render_template('reader_info.html', user = user)

#U___
# for test by g.user
@app.route('/reader/modify', methods=['GET', 'POST'])
def reader_modify():
	global CURRENT_READER
	reader_judge()
	error = None
	user = query_db('''select * from users where user_num = ?''', [g.user], one=True)
	id = user[0]
	if request.method == 'POST':
		if not request.form['usernum']:
			error = 'You have to input your number'
		elif not request.form['password']:
			db = get_db()
			db.execute('''update users set email=? where user_id=? ''', [request.form['email'], id])
			db.commit()
			return redirect(url_for('reader_info'))
		else:
			db = get_db()
			db.execute('''update users set pwd=?\
				, email=? where user_id=? ''', [request.form['username'],
					generate_password_hash(request.form['password']),
				request.form['email'], id])
			db.commit()
			return redirect(url_for('reader_info'))
	return render_template('reader_modify.html', user=user, error = error)

#_B__
@app.route('/reader/query', methods=['GET', 'POST'])
def reader_query():
	global CURRENT_READER
	reader_judge()
	error = None
	books = None
	#print(111)
	if request.method == 'POST':
		if request.form['item'] == 'name':
			if not request.form['query']:
				error = 'You have to input the book name'
			else:
				ini_id = (request.form['query'])
				print('ini_id:',ini_id)
				matchid = '%' + ini_id + '%'
				print('matchid:',matchid)
				#books = query_db('''select * from books where book_name = ?''',[request.form['query']])
				books = query_db('''select * from books where book_name like ? ''',[matchid])
				if not books:
					error = 'Invalid book name'
		else:
			if not request.form['query']:
				error = 'You have to input the book author'
			else:
				ini_id = (request.form['query'])
				print('ini_id:',ini_id)
				matchid = '%' + ini_id + '%'
				print('matchid:',matchid)
				#books = query_db('''select * from books where author = ?''',[request.form['query']])
				books = query_db('''select * from books where author like ? ''',[matchid])
				if not books:
					error = 'Invalid book author'
	print("books:",books)
	return render_template('reader_query.html', books = books, error = error)

#_BLH
@app.route('/reader/book/<id>', methods=['GET', 'POST'])
def reader_book(id):
	global CURRENT_READER
	reader_judge()
	error = None
	book = query_db('''select * from books where book_id = ?''', [id], one=True)
	reader = query_db('''select * from borrows where book_id = ?''', [id], one=True)
	count  = query_db('''select count(book_id) from borrows where user_num = ? ''',
			  [g.user], one = True)
	current_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
	return_time = time.strftime('%Y-%m-%d',time.localtime(time.time() + 2600000))
	print(current_time)
	if request.method == 'POST' or request.method == 'GET':
		#print(1)
		if reader:
			error = 'The book has already borrowed.'
		else:
			if count[0] == 3:
				error = 'You can\'t borrow more than three books.'
			else:
				print(g,[g.user, id,current_time, return_time])
				db = get_db()
				db.execute('''insert into borrows (user_num, book_id, date_borrow, \
					date_return) values (?, ?, ?, ?) ''', [g.user, id,
										   current_time, return_time])
				db.execute('''insert into histroys (user_num, book_id, date_borrow, \
					status) values (?, ?, ?, ?) ''', [g.user, id,
										   current_time, 'not return'])
				db.commit()
				return redirect(url_for('reader_book', id = id))
		return render_template('reader_book.html', book = book, reader = reader, error = error)

#___H
@app.route('/reader/histroy', methods=['GET', 'POST'])
def reader_histroy():
	global CURRENT_READER
	reader_judge()
	histroys = query_db('''select * from histroys, books where histroys.book_id = books.book_id and histroys.user_num=? ''', [g.user], one = False)

	return render_template('reader_histroy.html', histroys = histroys)

