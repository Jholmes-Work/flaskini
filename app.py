from flask import Flask, jsonify, request, url_for, redirect, session, render_template, g
import sqlite3

app = Flask(__name__)

def connect_db():
    sql = sqlite3.connect('data.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

app.config['DEBUG'] = True
#Makes it so users can't modify session, should be radom (don't put sensentive info in session)
app.config['SECRET_KEY'] = 'Thisisasecret!'

@app.route('/')
def index():
    session.pop('name', None)
    return '<h1>Hello World!</h1>'

@app.route('/home', methods=['POST', 'GET'], defaults={'name' : 'default'})
@app.route('/home/<string:name>', methods=['POST', 'GET'])
def home(name):
    session['name'] = name
    return render_template('home.html', name=name, display=True, mylist=['one', 'two', 'three', 'four'], 
                           listofdict=[{'name' : 'Zach'}, {'name': 'Zoey'}])

@app.route('/json')
def json():
    if 'name' in session:
        name = session['name']
    else:
        name = 'Not in session'
    return jsonify({'key' : 'value', 'listkey' : [1,2,3], 'name': name})

@app.route('/query')
def query():
    name = request.args.get('name')
    location = request.args.get('location')
    return '<h1>Hi {}.  You are from {}. You are on the query page!</h1>.'.format(name, location)

@app.route('/theform', methods=['GET', 'POST'])
def theform():
    
    if request.method == 'GET':
        return  render_template('form.html')
    else:
        name = request.form['name']
        location= request.form['location']

        db = get_db()
        db.execute('insert into users (name, location) values (?, ?)', [name, location])
        db.commit()

        #return 'Hello {}.  You are from {}.  You have submitted the form sucessfully!'.format(name, location)
        return redirect(url_for('home', name=name, Location=location))
'''
@app.route('/process', methods=['POST'])
def process():
    name = request.form['name']
    location= request.form['location']

    return 'Hello {}.  You are from {}.  You have submitted the form sucessfully!'.format(name, location)
'''
@app.route('/processjson', methods=['POST'])
def processjson():

    data = request.get_json()

    name = data['name']
    location = data['location']
    randomlist = data['randomlist']

    return jsonify({'result' : 'Success', 'name' : name, 'location' : location, 'randomkeyinlist' : randomlist[1]})

@app.route('/viewresults')
def viewresults():
    db = get_db()
    cur = db.execute('select id, name, location from users')
    results = cur.fetchall()
    return '<h1>The ID is {}.  The name is {}.  The location is {}</h1>'.format(results[2]['id'], results[2]['name'], results[2]['location'])


if __name__ == '__main__':
    app.run()