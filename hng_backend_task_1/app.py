from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


@app.route('/api/hello', methods=['GET'])
def hello():
    visitor_name = request.args.get('visitor_name', 'Guest')
    client_ip = request.remote_addr

    # Fetch location data
    location_response = requests.get(f'http://ipinfo.io/{client_ip}/json')
    location_data = location_response.json()
    city = location_data.get('city', 'Unknown')
    location = city

    temperature = 11  # Placeholder for temperature fetching logic
    greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celcius in {location}"

    response = {
        "client_ip": client_ip,
        "location": location,
        "greeting": greeting
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
