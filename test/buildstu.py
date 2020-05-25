from werkzeug.security import check_password_hash, generate_password_hash
from re import match
if __name__ == '#__main__':
	with open('namelist.txt','w') as f:
		for i in range(1,31):
			if i < 10:
				f.write("%d|219040010%d|%s|219040010%d@stu.hit.edu.cn\n" % (i,i,generate_password_hash('219040010%d'%i),i))
			else:
				f.write("%d|21904001%d|%s|21904001%d@stu.hit.edu.cn\n" % (i,i,generate_password_hash('21904001%d'%i),i))

def isnum(cand):
	num_pat = r'[2,L][0-9]{8}'
	grad_pat = r'[0-9]{2}[S,B][0-9]{7}'
	try:
		a = match(num_pat,cand)
		b = match(grad_pat,cand)
		#print(a,b)
		return (a is not None) or (b is not None)
	except:
		return false


if __name__ == '__main__':
	print(isnum(input()))
	
