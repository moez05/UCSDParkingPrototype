from flask import Flask, request, render_template, g, redirect, url_for
import os, sqlite3, arrow

app = Flask(__name__, template_folder='views')
DATABASE = os.path.dirname(os.path.abspath(__file__)) + '/data/database.db'

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/arriving", methods=['GET', 'POST'])
def arriving():
    if request.method == 'GET':
        users = query_db('select * from posts order by time_till_departure asc')
        user_dicts = []
        for u in users:
            leave_time = arrow.get(u[4])
            user_dicts.append({
                'parking_lot': u[0],
                'floor': u[1],
                'location': getLocationString(u[2]),
                'spot_type': getSpotTypeString(u[3]),
                'time_till_departure': leave_time.humanize(arrow.utcnow()),
                'details': u[5]
            })
        return render_template('arriving.html', user_dicts=user_dicts)

@app.route("/leaving", methods=['GET', 'POST'])
def leaving():
    if request.method == 'GET':
        return render_template('leaving.html')
    if request.method == 'POST':

        leave_time = arrow.utcnow().replace(minutes = +int(request.form['time']))

        save_post(request.form['parking-lot'],
                  request.form['floor'],
                  str(getLocationInt(request.form['location'])),
                  str(getSpotTypeInt(request.form['spot-type'])),
                  leave_time.timestamp,
                  request.form['details']
                 )

        return redirect(url_for('arriving'))

def getLocationInt(location):
    locationMap = {
        "north": 1,
        "north-east": 2,
        "east": 3,
        "south-east": 4,
        "south": 5,
        "south-west": 6,
        "west" : 7,
        "north-west": 8
        # TODO: insert more options later
    }

    return locationMap[location]

def getLocationString(location):
    locationMap = {
        1: "North",
        2: "North-East",
        3: "East",
        4: "South-East",
        5: "South",
        6: "South-West",
        7: "West",
        8: "North-West"
        # TODO: insert more options later
    }

    return locationMap[location]

def getSpotTypeInt(spotType):
    spotTypeMap = {
        "A": 1,
        "B": 2,
        "S": 3,
        "V": 4,
        "VP": 5
    }

    return spotTypeMap[spotType]

def getSpotTypeString(spotType):
    spotTypeMap = {
        1: "A",
        2: "B",
        3: "S",
        4: "V",
        5: "VP"
    }

    return spotTypeMap[spotType]


## DATABASE STUFF ##

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def save_post(parking_lot, floor, location, spot_type, time_till_departure, details):
    db = get_db()
    db.cursor().execute("insert into posts (parking_lot, floor, location, spot_type, time_till_departure, details) values (?,?,?,?,?,?)", (parking_lot, floor, location, spot_type, time_till_departure, details))
    db.commit()
    close_db(None)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def connect_to_database():
    return sqlite3.connect(DATABASE)



if __name__ == "__main__":
    app.run(debug=True, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
