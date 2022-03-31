from replit import db

keys = db.keys()
for key in keys:
	print(key + ', ' + db[key])