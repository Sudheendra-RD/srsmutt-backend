from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import requests, os
import datetime
from bs4 import BeautifulSoup
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime
import pytz
from mangum import Mangum

# current_date = datetime.now().strftime("%Y-%m-%d")
# qweqwe = '2025-01-25'
# form_data = {
#     'date': '2025-01-25',  # Add current date
# }

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes by default

@app.route('/proxy', methods=['POST'])
def proxy():
    target_url = "https://srsmatha.org/srsbook/code.php?page=app/panchdata"
    
    # Extract form data from the incoming request
    form_data = request.form.to_dict()
    
    # Forward the request to the target URL
    try:
        response = requests.post(target_url, data=form_data)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract "Masa Niyamaka"
        masa_niyamaka = soup.find('div', class_='manasa').contents[1].strip()
        # Extract "Samvastara"
        samvatsara_arr = soup.find('div', class_='sams').contents[0].split(', ')
        samvatsara = samvatsara_arr[0]
        ayana = samvatsara_arr[1]
        ruthu = samvatsara_arr[2]
        masa = samvatsara_arr[3]
        paksha = samvatsara_arr[4]
        tithi = soup.find('div', class_='thithi').contents[0]
        vasara_nakshatra_yoga_karna_arr = soup.find('div', class_='dys').contents
        vasara = vasara_nakshatra_yoga_karna_arr[0]
        nakshatra = vasara_nakshatra_yoga_karna_arr[2]
        yoga = vasara_nakshatra_yoga_karna_arr[4]
        karna = vasara_nakshatra_yoga_karna_arr[6]
        today_special = ''
        if (len(soup.find('div', class_='mtitle').contents) > 1):
            today_special = soup.find('div', class_='mtitle').contents[1]
        final_arr = soup.find_all('div', class_='txt')
        try:
            sunrise = get_sunrise_sunset_time('rise', form_data['date'])
        except IndexError:
            sunrise = ''
        try:
            sunset = get_sunrise_sunset_time('set', form_data['date'])
        except IndexError:
            sunset = ''
        try:
            shraddha_tithi = final_arr[2].contents[1]
        except IndexError:
            shraddha_tithi = ''
        try:
            rahukala = get_rahukala(vasara)
        except IndexError:
            rahukala = ''
        try:
            gulika_kala = get_gulika_kala(vasara)
        except IndexError:
            gulika_kala = ''
        try:
            yamaganda_kala = get_yamaganda_kala(vasara)
        except IndexError:
            yamaganda_kala = ''
            
        response_json = {
            'samvatsara': samvatsara,
            'ayana': ayana,
            'ruthu': ruthu,
            'masa': masa,
            'paksha': paksha,
            'masaniyamaka': masa_niyamaka,
            'tithi': tithi,
            'vasara': vasara,
            'nakshatra': nakshatra,
            'yoga': yoga,
            'karna': karna,
            'today_special': today_special,
            'sunrise': sunrise,
            'sunset': sunset,
            'shraddha_tithi': shraddha_tithi,
            'rahukala': rahukala,
            'gulika_kala': gulika_kala,
            'yamaganda_kala': yamaganda_kala
        }
        # Create a response with the proxied content
        proxied_response = Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'text/html')  # Default to text/html if Content-Type is missing
        )
        
        # Add custom headers
        proxied_response.headers['Custom-Header'] = 'CustomValue'
        proxied_response.headers['Access-Control-Allow-Origin'] = '*'
        proxied_response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        proxied_response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response_json
    
    except requests.RequestException as e:
        # Handle errors
        return jsonify({
            "error": "Failed to forward the request:",
            "details": str(e)
        }), 500

def get_rahukala(vasara):
    match vasara:
        case 'Monday':
            return '07:30 AM - 09:00 AM'
        case 'Tuesday':
            return '03:00 PM - 04:30 PM'
        case 'Wednesday':
            return '12:00 PM - 01:30 PM'
        case 'Thursday':
            return '01:30 PM - 03:00 PM'
        case 'Friday':
            return '10:30 AM - 12:00 PM'
        case 'Saturday':
            return '09:00 AM - 10:30 AM'
        case 'Sunday':
            return '04:30 PM - 06:00 PM'
        
def get_gulika_kala(vasara):
    match vasara:
        case 'Monday':
            return '01:30 PM - 03:00 PM'
        case 'Tuesday':
            return '12:00 PM - 01:30 PM'
        case 'Wednesday':
            return '10:30 AM - 12:00 PM'
        case 'Thursday':
            return '09:00 AM - 10:30 AM'
        case 'Friday':
            return '07:30 AM - 09:00 AM'
        case 'Saturday':
            return '06:00 AM - 07:30 AM'
        case 'Sunday':
            return '03:00 PM - 04:30 PM'

def get_yamaganda_kala(vasara):
    match vasara:
        case 'Monday':
            return '10:30 AM - 12:00 PM'
        case 'Tuesday':
            return '09:00 AM - 10:30 AM'
        case 'Wednesday':
            return '07:30 AM - 09:00 AM'
        case 'Thursday':
            return '06:00 AM - 07:30 AM'
        case 'Friday':
            return '03:00 PM - 04:30 PM'
        case 'Saturday':
            return '01:30 PM - 03:00 PM'
        case 'Sunday':
            return '12:00 PM - 01:30 PM'
        
def get_sunrise_sunset_time(rise_or_set, date):
    # Define Bangalore location
    bangalore = LocationInfo(name="Bangalore", region="India", timezone="Asia/Kolkata", latitude=12.9716, longitude=77.5946)

    try:
        # Parse the input date
        custom_date = datetime.strptime(date, "%Y-%m-%d").date()
        
        # Get sunrise and sunset times
        s = sun(bangalore.observer, date=custom_date, tzinfo=bangalore.timezone)

    except ValueError:
        print("Invalid date format. Please enter the date in YYYY-MM-DD format.")

    # Format the IST times as HH:MM AM/PM.
    if rise_or_set == 'rise':
        return s['sunrise'].strftime('%I:%M:%S %p')
    else:
        return s['sunset'].strftime('%I:%M:%S %p')

handler = Mangum(app)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
#     # app.run(debug=True, host='0.0.0.0', port=5000)

