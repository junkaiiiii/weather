from flask import Flask, request, render_template,redirect
import requests
from config import API
from models import db, City
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/", methods=["POST","GET"])
def index():
    if request.method == "POST":
        new_city = request.form['city'].strip()
        if new_city:
            exist_city = City.query.filter_by(name=new_city).first()

            if exist_city:
                return redirect('/')
            
            available_city = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={new_city}&limit=1&appid={API}")
            
            print(available_city.text)
            print(available_city.status_code)

            if available_city.status_code == 200:
                db.session.add(City(name = available_city.json()[0]['name']))
                db.session.commit()
        return redirect('/')

    cities = City.query.all()
    weathers = []

    for city in cities:
        print(city)
        pos_response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city.name}&limit=5&appid={API}")
        city_pos = pos_response.json()

        print(city_pos)

        if not city_pos:
            db.session.delete(city)
            db.session.commit()
            continue 

        
        lat = city_pos[0]['lat']
        lon = city_pos[0]['lon']
        response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=metric&appid={API}")

        if response.status_code == 200:
            data = response.json()
            weathers.append({
                'city_id' : city.id,
                'city' : city.name,
                'temp' : data["current"]["temp"],
                'feels_like' : data["current"]["feels_like"],
                'weather' : data["current"]["weather"][0]["main"],
                "icon" : data["current"]["weather"][0]["icon"]
            })
    return render_template("index.html",weathers = weathers)

@app.route("/delete/<int:city_id>",methods=["POST"])
def delete(city_id):
    city = City.query.get_or_404(city_id)
    db.session.delete(city)
    db.session.commit()
    return redirect('/')

@app.route("/city/<int:city_id>",methods=["GET"])
def city_details(city_id):
    city = City.query.get_or_404(city_id)
    response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city.name}&limit=5&appid={API}")
    city_pos = response.json()
    lat = city_pos[0]['lat']
    lon = city_pos[0]['lon']
    response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=metric&exclude=minutely,alerts&appid={API}")
    data = response.json()

    hourly = data['hourly'][0:10]
    time = int(datetime.now().strftime("%H"))

    daily = data['daily'][0:7]
    day_index = datetime.now().weekday()
    
    return render_template("city_details.html", city = city.name, hourly = hourly, cur_time = time, days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],day_index=day_index, daily=daily)



if __name__ == '__main__':
    app.run(debug=True)
    