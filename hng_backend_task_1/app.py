from flask import Flask, request, jsonify
import ipinfo
import pyowm

app = Flask(__name__)

ipinfo_access_token = 'd693024da67f65'
weather_api_key = 'fa566a26483a061a7b67eb9727cbce9e'

ipinfo_handler = ipinfo.getHandler(ipinfo_access_token)
owm = pyowm.OWM(weather_api_key)


@app.route('/api/hello', methods=['GET'])
def hello():
    visitor_name = request.args.get('visitor_name', 'Guest')
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]

    # Fetch location data
    try:
        location_data = ipinfo_handler.getDetails(client_ip)
        city = getattr(location_data, 'city', 'Unknown')
    except Exception as e:
        city = 'Unknown'
        print(f"Error fetching location data: {e}")

    location = city

    # Fetch temperature data
    try:
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(location)
        weather = observation.weather
        temperature = weather.temperature('celsius')['temp']
    except Exception as e:
        temperature = 'unknown'
        print(f"Error fetching weather data: {e}")

    greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {location}"

    response = {
        "client_ip": client_ip,
        "location": location,
        "greeting": greeting
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
