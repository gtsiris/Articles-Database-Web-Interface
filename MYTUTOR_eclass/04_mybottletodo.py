from bottle import route, run
import sys, os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))

@route('/todo')
def todo():
    db = pymysql.connect('127.0.0.1', 'root', '', 'testdb')#replace with your values
    cursor = db.cursor()
    cursor.execute("SELECT task FROM todo WHERE status LIKE '1'")
    result = cursor.fetchall()
    return str(result)

#add this at the very end: By enabling debug, you will get a full stacktrace of the Python interpreter, which usually contains useful information for finding bugs.

run(host='localhost', port=8080, debug=True)
