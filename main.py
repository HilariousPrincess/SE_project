# -*- coding: utf-8 -*-
#from user import *
import time
import re
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
	 render_template, abort, g, flash, _app_ctx_stack
from werkzeug.security import check_password_hash, generate_password_hash


#CONFIGURATION
DATABASE = 'book.db'
DEBUG = True
SECRET_KEY = 'development key'
MANAGER_NAME = 'admin'
MANAGER_PWD = '123456'
CURRENT_READER = ''

app = Flask(__name__)

app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('book.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def query_db(query, args=(), one=False):
	cur = get_db().execute(query, args)
	rv = cur.fetchall()
	return (rv[0] if rv else None) if one else rv

def get_db():
	top = _app_ctx_stack.top
	if not hasattr(top, 'sqlite_db'):
		top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
		top.sqlite_db.row_factory = sqlite3.Row
	return top.sqlite_db
	
def add_book(ISBN,num):
	query = '''update books b set b.total_num = b.total_num + ?, b.present_num = b.present_num + ? where b.book_id = ?'''
	db = get_db()
	db.execute(query,[num,num,ISBN])
	de.commit()

@app.teardown_appcontext
def close_database(exception):
	top = _app_ctx_stack.top
	if hasattr(top, 'sqlite_db'):
		top.sqlite_db.close()

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = session['user_id']

@app.route('/')
def index():
	return render_template('index.html')

#U___
@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	email_pat = r'^[0-9a-zA-Z_]{0,19}@[.0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$'
	num_pat = r'2[0-9]{8}'
	'''
	usernum = request.form['usernum']
	pwd = request.form['password']
	pwd2 = request.form['password2']
	email = request.form['email']
	'''
	if request.method == 'POST':
		usernum = request.form['usernum']
		pwd = request.form['password']
		pwd2 = request.form['password2']
		email = request.form['email']
		if not usernum:
			error = 'You have to enter a usernum'
		elif re.match(num_pat,usernum) is None:
			error = 'Invalid number!'
		elif not pwd:
			error = 'You have to enter a password'
		elif pwd != pwd2:
			error = 'The two passwords do not match'
		elif get_user_id(usernum) is not None:
			error = 'The username is already taken'
		elif re.match(email_pat,email) is None:
			error = 'Invalid email address'
		elif len(pwd) < 6 or len(pwd) > 20:
			error = 'The length of the password should between 6 and 20'
		else:
			db = get_db()
			db.execute('''insert into users (user_num, pwd, email) \
				values (?, ?, ?) ''', [usernum, generate_password_hash(
				pwd), request.form['email']])
			db.commit()
			return redirect(url_for('manager'))
	return render_template('register.html', error = error)

@app.route('/logout')
def logout():
	session.pop('user_id', None)
	return redirect(url_for('index'))


#U___
@app.route('/reader_login', methods=['GET', 'POST'])
def reader_login():
	global CURRENT_READER
	error = None
	if request.method == 'POST':
		num = request.form['user_num']
		print(num)
		print(request.form['password'])
		user = query_db('''select * from users where user_num = ?''',
				[request.form['user_num']], one=True)
		if user is None:
			error = 'Invalid username'
		elif not check_password_hash(user['pwd'], request.form['password']):
			error = 'Invalid password'
		else:
			session['user_id'] = user['user_num']
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
	rv = query_db('select user_id from users where user_num = ?',
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
	email_pat = r'^[0-9a-zA-Z_]{0,19}@[.0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$'
	user = query_db('''select * from users where user_num = ?''', [g.user], one=True)
	id = user[0]
	if request.method == 'POST':
		'''
		if not request.form['usernum']:
			error = 'You have to input your number'
		'''
		if not request.form['password']:
			if request.form['email']:
				if re.match(email_pat,email) is None:
					error = 'Invalid email address'
				else:
					db = get_db()
					db.execute('''update users set email=? where user_id=? ''', [request.form['email'], id])
					db.commit()
					return redirect(url_for('reader_info'))
		else:
			db = get_db()
			db.execute('''update users set pwd=?\
				, email=? where user_id=? ''', [generate_password_hash(request.form['password']),
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
		print(reader)
		if reader and reader != g.user:
			error = 'The book has already borrowed.'
		else:
			#if count[0] == 3:
			#	error = 'You can\'t borrow more than three books.'
			if count[0] < 3:
				#print(g,[g.user, id,current_time, return_time])
				db = get_db()
				db.execute('''insert into borrows (user_num, book_id, date_borrow, \
					date_return) values (?, ?, ?, ?) ''', [g.user, id,
										   current_time, return_time])
				db.execute('''insert into histroys (user_num, book_id, date_borrow, \
					status) values (?, ?, ?, ?) ''', [g.user, id,
										   current_time, 'not return'])
				db.execute('''update books set present_num = present_num - 1 where book_id = ?''',[id])
				db.commit()
				return redirect(url_for('reader_book', id = id))
			else:
				error = 'You can\'t borrow more than three books.'
		return render_template('reader_book.html', book = book, reader = reader, error = error)

#___H
@app.route('/reader/histroy', methods=['GET', 'POST'])
def reader_histroy():
	global CURRENT_READER
	reader_judge()
	histroys = query_db('''select * from histroys, books where histroys.book_id = books.book_id and histroys.user_num=? ''', [g.user], one = False)

	return render_template('reader_histroy.html', histroys = histroys)


@app.route('/manager_login', methods=['GET', 'POST'])
def manager_login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['MANAGER_NAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['MANAGER_PWD']:
			error = 'Invalid password'
		else:
			session['user_id'] = app.config['MANAGER_NAME']
			return redirect(url_for('manager'))
	return render_template('manager_login.html', error = error)


# 添加简单的安全性检查
def manager_judge():
	if not session['user_id']:
		error = 'Invalid manager, please login'
		return render_template('manager_login.html', error = error)

@app.route('/manager/books')
def manager_books():
	manager_judge()
	return render_template('manager_books.html',
			books = query_db('select * from books', []))

@app.route('/manager')
def manager():
	manager_judge()
	return render_template('manager.html')

#U___
@app.route('/manager/users')
def manager_users():
	manager_judge()
	users = query_db('''select * from users''', [])
	return render_template('manager_users.html', users = users)

#U___
@app.route('/manager/user/modify/<id>', methods=['GET', 'POST'])
def manger_user_modify(id):
	user_judge()
	error = None
	user = query_db('''select * from users where user_id = ?''', [id], one=True)
	if request.method == 'POST':
		if not request.form['password']:
			db = get_db()
			db.execute('''update users set email=? where user_id=? ''', [request.form['email'], id])
			db.commit()
			return redirect(url_for('manager_user', id = id))
		else:
			db = get_db()
			db.execute('''update users set pwd=?,email=? \
			where user_id=? ''',[generate_password_hash(request.form['password']), request.form['email'], id])
			db.commit()
			return redirect(url_for('manager_user', id = id))
	return render_template('manager_user_modify.html', user=user, error = error)

#U___
@app.route('/manager/user/deleter/<id>', methods=['GET', 'POST'])
def manger_user_delete(id):
	manager_judge()
	db = get_db()
	db.execute('''delete from users where user_id=? ''', [id])
	db.commit()
	return redirect(url_for('manager_users'))

#_B__
@app.route('/manager/books/add', methods=['GET', 'POST'])
def manager_books_add():
	manager_judge()
	error = None
	if request.method == 'POST':
		if not request.form['id']:
			error = 'You have to input the book ISBN'
		elif not request.form['name']:
			error = 'You have to input the book name'
		elif not request.form['author']:
			error = 'You have to input the book author'
		elif not request.form['company']:
			error = 'You have to input the publish company'
		elif not request.form['date']:
			error = 'You have to input the publish date'
		elif not request.form['num']:
			error = 'You have to input the number'
		else:
			db = get_db()
			print('Q:',query_db('''select * from books where book_id = ?''',[request.form['id']]))
			if query_db('''select * from books where book_id = ?''',[request.form['id']]) == []:
				print(1)
				db.execute('''insert into books (book_id, book_name, author, publish_com,publish_date, total_num, present_num) values (?, ?, ?, ?, ?, ?, ?) ''', [request.form['id'],request.form['name'], request.form['author'], request.form['company'],request.form['date'],request.form['num'],request.form['num']])
				print(2)
				db.commit()
				print(3)
			else:
				db.execute('''update books set total_num = total_num + ?, present_num = present_num + ? where book_id = ?''',[request.form['num'],request.form['num'],request.form['id']])
				db.commit()
				print(5)
			print(4)
			return redirect(url_for('manager_books'))
	return render_template('manager_books_add.html', error = error)

#_B__
@app.route('/manager/books/delete', methods=['GET', 'POST'])
def manager_books_delete():
	manager_judge()
	error = None
	if request.method == 'POST':
		if not request.form['id']:
			error = 'You have to input the book name'
		else:
			book = query_db('''select * from books where book_id = ?''',
				[request.form['id']], one=True)
			if book is None:
				error = 'Invalid book id'
			else:
				db = get_db()
				db.execute('''delete from books where book_id=? ''', [request.form['id']])
				db.commit()
				return redirect(url_for('manager_books'))
	return render_template('manager_books_delete.html', error = error)

#_BLH
@app.route('/manager/books/return', methods=['GET', 'POST'])
def manager_books_return():
	manager_judge()
	error = None
	current_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
	if request.method == 'POST':
		NUM = request.form['num']
		ISBN = request.form['ISBN']
		print('num:',NUM,'\nISBN:',ISBN)
		if not NUM:
			error = 'You have to input the number'
		elif not ISBN:
			error = 'You have to input the ISBN'
		else:
			#db = get_db()
			#cur = db.execute('''select * from borrows where book_id = "1" and user_num = "2170700212"''')
			#ans = cur.fetchall()
			#ans = query_db('''select * from borrows where book_id = ? and user_num = ?''',[NUM,ISBN],one = True)
			ans = query_db('''select * from borrows where book_id = %s and user_num = %s''' % (NUM,ISBN))
			print('ans:',ans)
			if ans is None:
				error = 'Invalid information'
			else:
				db = get_db()
				print('update begin')
				db.execute('''update histroys set status = ?, date_return = ?  where book_id=? and user_num=? and status=? ''',['returned', current_time, ISBN, NUM, 'not return'])
				db.execute('''delete from borrows where book_id = ? and user_num = ?''' , [ISBN,NUM])
				db.execute('''update books set present_num = present_num + 1 where book_id = ?''',[ISBN])
				print('update ends')
				db.commit()
			#tmp = query_db('''select * from borrows where book_id = ? and user_num = ?''',[request.form['ISBN'],request.form['num']])
			print(1)
	return render_template('manager_books_return.html', error = error)
		

#_BLH
@app.route('/manager/book/<id>', methods=['GET', 'POST'])
def manager_book(id):
	manager_judge()
	#book = query_db('''select * from books where book_id = ?''', [id], one=True)
	#reader = query_db('''select * from borrows where book_id = ?''', [id], one=True)
	#num = query_db('''select user_num from borrows where book_id = ?''', [id], one=True)
	#print('book:',book)
	#print('reader:',reader)
	#print('num:',num)
	return '111'
	#if num == None:
	#	return 'No borrowers.'
	
	#current_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
	#if request.method == 'POST' or request.method == 'GET':
	#	return 'Huaji'
		#if True: #False and request.form['user_num']:
			#db = get_db()
			#print(['retruned', current_time, id, name[0], 'not return'])
			#print(1)
			#db.execute('''update histroys set status = ?, date_return = ?  where book_id=? and user_num=? and status=? ''',['returned', current_time, id, request.form['user_num'], 'not return'])
			#db.execute('''delete from borrows where book_id = ? and user_num = ?''' , [id,request.form['user_num']])
			#db.execute('''update books b set b.present_num = b.present_num + 1 where b.book_id = ?''',[id])
			#db.commit()
			#return redirect(url_for('manager_book', id = id))
			#return render_template('manager_book.html', book = book, reader = reader)

#U___	
@app.route('/manager/user/<id>', methods=['GET', 'POST'])
def manager_user(id):
	manager_judge()
	user = query_db('''select * from users where user_id = ?''', [id], one=True)
	books = None
	return render_template('manager_userinfo.html', user = user, books = books)

#_B__
@app.route('/manager/books/update', methods=['GET', 'POST'])
def manager_books_update():
	manager_judge()
	error = None
	#book = query_db('''select * from books where book_id = ?''', [id], one=True)
	if request.method == 'POST':
		if not request.form['ISBN']:
			error = 'You have to input the ISBN'
		if not request.form['name']:
			error = 'You have to input the book name'
		elif not request.form['author']:
			error = 'You have to input the book author'
		elif not request.form['company']:
			error = 'You have to input the publish company'
		elif not request.form['date']:
			error = 'You have to input the publish date'
		else:
			db = get_db()
			db.execute('''update books set book_name=?, author=?, publish_com=?, publish_date=? where book_id=? ''', [request.form['name'], request.form['author'], request.form['company'], request.form['date'], request.form['ISBN']])
			db.commit()
			return redirect(url_for('manager_books'))
	return render_template('manager_books_update.html', error = error)

#_B__
@app.route('/manager/modify/<id>', methods=['GET', 'POST'])
def manager_modify(id):
	manager_judge()
	error = None
	book = query_db('''select * from books where book_id = ?''', [id], one=True)
	if request.method == 'POST':
		if not request.form['name']:
			error = 'You have to input the book name'
		elif not request.form['author']:
			error = 'You have to input the book author'
		elif not request.form['company']:
			error = 'You have to input the publish company'
		elif not request.form['date']:
			error = 'You have to input the publish date'
		else:
			db = get_db()
			db.execute('''update books set book_name=?, author=?, publish_com=?, publish_date=? where book_id=? ''', [request.form['name'], request.form['author'], request.form['company'], request.form['date'], id])
			db.commit()
			return redirect(url_for('manager_book', id = id))
	return render_template('manager_modify.html', book = book, error = error)


if __name__ == '__main__':
	init_db()
	app.run(debug=True)



