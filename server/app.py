from flask import Flask, render_template, request, json
from flaskext.mysql import MySQL
import config

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = config.mysqluser
app.config['MYSQL_DATABASE_PASSWORD'] = config.mysqlpass
app.config['MYSQL_DATABASE_DB'] = config.mysqldb
mysql.init_app(app)


@app.route("/")
def main():
        return render_template('index.html')


@app.route("/insertrecord", methods=['POST'])
def insertRecord():
    _tab = request.form['table']
    _m = request.form['month']
    _d = request.form['day']
    _t = request.form['title']
    _a = request.form['artist']
    _r = request.form['relyear']

    if _tab and _m and _d and _t and _a and _r:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('insertRecord', (_tab, _m, _d, _t, _a, _r))

        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            return json.dumps({'message' : 'record successfully inserted'})
        else:
            return json.dumps({'error' : str(data[0])})
    else:
        return json.dumps({'error': 'error with inputted info'})


# @app.route("showrecords", methods=['GET'])
# def showRecords():
#     _tab = request.form['table']
#     if _tab:
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         cursor.callproc('showrecords', (_tab,))
#
#         data = cursor.fetchall()
#         if len(data) is 0:
# 			conn.commit()
# 			return json.dumps({'message' : 'successfully called'})
#         else:
# 			return json.dumps({'error' : str(data[0])})



if __name__ == "__main__":
        app.debug = True
        app.run()
