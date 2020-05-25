# -*- coding: utf-8 -*-
from user import *


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
		else:
			db = get_db()
			db.execute('''insert into books (book_id, book_name, author, publish_com,
				publish_date) values (?, ?, ?, ?, ?) ''', [request.form['id'],
					request.form['name'], request.form['author'], request.form['company'],
				request.form['date']])
			db.commit()
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
@app.route('/manager/book/<id>', methods=['GET', 'POST'])
def manager_book(id):
	manager_judge()
	book = query_db('''select * from books where book_id = ?''', [id], one=True)
	reader = query_db('''select * from borrows where book_id = ?''', [id], one=True)
	num = query_db('''select user_num from borrows where book_id = ?''', [id], one=True)
	if num == None:
		return 'No borrowers.'
	current_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
	#print(num)
	if request.method == 'POST' or request.method == 'GET':
		db = get_db()
		#print(['retruned', current_time, id, name[0], 'not return'])
		db.execute('''update histroys set status = ?, date_return = ?  where book_id=?
			and user_num=? and status=? ''',
			   ['returned', current_time, id, num[0], 'not return'])
		db.execute('''delete from borrows where book_id = ? ''' , [id])
		db.commit()
		#return redirect(url_for('manager_book', id = id))
		return render_template('manager_book.html', book = book, reader = reader)

#U___	
@app.route('/manager/user/<id>', methods=['GET', 'POST'])
def manager_user(id):
	manager_judge()
	user = query_db('''select * from users where user_id = ?''', [id], one=True)
	books = None
	return render_template('manager_userinfo.html', user = user, books = books)

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

