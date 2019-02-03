from flask import Flask, render_template, request, json
from flaskext.mysql import MySQL
import config

import calendar

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = config.mysqluser
app.config['MYSQL_DATABASE_PASSWORD'] = config.mysqlpass
app.config['MYSQL_DATABASE_DB'] = config.mysqldb
mysql.init_app(app)


@app.route("/")
def main():
    return render_template('index.html')

@app.route("/insert")
def insertpage():
    return render_template('insert.html')

@app.route("/insertrecord", methods=['POST'])
def insertRecord():
    try:
        _tab = request.form['table']
        _m = request.form['month']
        _d = request.form['day']
        _t = request.form['title']
        _a = request.form['artist']
        _r = request.form['relyear']
    except Exception:
        return render_template('error.html', error_msg = "form data not submitted properly")

    if _tab and _m and _d and _t and _a and _r:
        conn = mysql.connect()
        cursor = conn.cursor()
        try:
            cursor.callproc('insertRecord', (_tab, _m, _d, _t, _a, _r))
        except Exception as e:
            return render_template('error.html', error_msg= str(e))

        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            return render_template('insert.html', success_msg="Nice tunes! Record successfully entered!")
        else:
            return render_template('error.html', error_msg= "no data was returned")
    else:
        return render_template('error.html', error_msg= "one or more form fields not filled out")

@app.route("/select")
def selectpage():
    return render_template('select.html')


@app.route("/showrecords", methods=['POST'])
def showRecords():
    try:
        _tab = request.form['table']
    except Exception:
        return render_template('error.html', error_msg = "you didn't select a table")

    if _tab:
        conn = mysql.connect()
        cursor = conn.cursor()
        try:
            cursor.callproc('selectrecords', (_tab,))
        except Exception as e:
            return render_template('error.html', error_msg=str(e))

        data = cursor.fetchall()

        if len(data) is 0:
            return render_template('error.html', error_msg = 'something happened: ' + str(data[0]))
        else:
            conn.commit()
            res_dict = []
            for row in data:
                row_dict = {
                    'Month' : calendar.month_name[row[0]],
                    'Day' : row[1],
                    'Album' : row[2],
                    'Artist' : row[3],
                    'Release_Year' : row[4]
                }
                res_dict.append(row_dict)
            return render_template('table_results.html', selected_table = _tab, results = res_dict)
    else:
        return render_template('error.html', error_msg = "some error occurred while selecting table")

@app.route("/albuminfo/<album>")
def getAlbum(album):
    return render_template('albuminfo.html', album_name = album)


if __name__ == "__main__":
        app.debug = True
        app.run()
