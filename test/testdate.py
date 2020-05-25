import re

years = range(1601,2001)
months = range(14)
dats = [-1,0,1,27,28,29,30,31,32]
date_t = '%d-%s-%s'
u10 = '0%s'
o10 = '%s'
date_s = ''
month = ''
day = ''

def isdate(s):
	date_pat = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
	try:
		if re.match(date_pat,s) is None:
			return False
		else:
			nleap = [31,28,31,30,31,30,31,31,30,31,30,31]
			leap = [31,29,31,30,31,30,31,31,30,31,30,31]
			year = int(s[0])*1000+int(s[1])*100+int(s[2])*10+int(s[3])
			month = int(s[5])*10+int(s[6])
			day = int(s[8])*10+int(s[9])
			if month > 12 or month <= 0:
				return false
			if year % 400 == 0 or (year % 100 != 0 and year % 4 == 0):
				return day <= leap[month] and day > 0
			else:
				return day <= nleap[month] and day > 0
	except:
		return False

if __name__ == '__main__':
	with open('test_date.txt','w') as f:
		for d in dats:
			for m in months:
				for y in years:
					if m < 10:
						month = u10 % m
					else:
						month = o10 % m
					if d >= 10:
						day = o10 % d
					else:
						day = u10 % d
					date_s = date_t % (y,month,day)
					f.write('%s is a valid date? %s\n' % (date_s,isdate(date_s))) 
					
