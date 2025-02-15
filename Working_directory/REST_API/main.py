import pymysql
from app import app
from db_config import mysql
from flask import jsonify
from flask import flash, request, session, redirect, url_for, g
from flask_httpauth import HTTPTokenAuth
from markupsafe import escape


auth = HTTPTokenAuth(scheme='Bearer')

tokens = {
    "qwertyuiop": "user1",
    "poiuytrewq": "user2"
}

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]


@app.route('/read', methods = ['GET', 'POST']) 
# @auth.login_required
def home():
	if(request.method == 'GET'):
		# print(mysql)
		conn = mysql.connect()
		# print (conn)
		print ("start")
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM corporate_actions")
		# cursor.execute("SHOW DATABASES")
		rows = cursor.fetchall()
		resp = jsonify(rows)
		resp.status_code = 200
		print (resp)
		return  resp
	else : 
		pass 



@app.route('/add/<int:num>/<string:company_name>', methods=['POST']) #<string:location>/
@auth.login_required
def add(num, company_name):
	try:
		if request.method == 'POST':

			sql = "INSERT INTO company_name VALUES( %s, %s)"
			data = (num,company_name)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			resp = jsonify('Added successfully!')
			resp.status_code = 200
			return resp
		else:
    			pass
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/update/<int:num>/<string:company_name>', methods=['PUT'])
@auth.login_required
def update(num, company_name):
	try:

		if request.method == 'PUT':
			
			sql = "UPDATE company_list SET name=%s WHERE id=%s"
			data = (company_name, num)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			resp = jsonify('User updated successfully!')
			resp.status_code = 200
			return resp
		else:
				print(" Incorrect method, update function failed")
				pass
			
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
		

@app.route('/delete/<int:num>', methods=['DELETE'])
@auth.login_required
def delete(num):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM company_list  WHERE id=%s", (num,))
		conn.commit()
		resp = jsonify('Deleted successfully!')
		resp.status_code = 200
		return resp
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
  
# driver function 
if __name__ == '__main__': 
	app.run(debug = True)
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	app.run()
	# app.run(debug=True, host='0.0.0.0')