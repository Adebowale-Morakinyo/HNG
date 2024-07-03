from flask import Flask, request, jsonify
import requests
import ipinfo

app = Flask(__name__)


access_token = 'd693024da67f65'



@app.route('/api/hello', methods=['GET'])
def hello():
    visitor_name = request.args.get('visitor_name', 'Guest')
    client_ip = request.remote_addr

    # Fetch location data
    location_response = ipinfo.getHandler(access_token)
    location_data = location_response.getDetails()
    city = location_data.city
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
