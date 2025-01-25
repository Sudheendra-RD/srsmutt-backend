from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import requests, os
from datetime import datetime
from bs4 import BeautifulSoup

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
        sunrise = final_arr[0].contents[1]
        sunset = final_arr[1].contents[1]
        shraddha_tithi = final_arr[2].contents[1]
        rahukala = final_arr[3].contents[1]
        gulika_kala = final_arr[4].contents[1]
        yamaganda_kala = final_arr[5].contents[1]
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    # app.run(debug=True, host='0.0.0.0', port=5000)

