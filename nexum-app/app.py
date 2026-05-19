from flask import Flask, render_template_string
import requests

app = Flask(__name__)
NASA_API_URL = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY'

@app.route('/')
def index():
    response = requests.get(NASA_API_URL).json()
    html = f'<h1>NASA Astronomy Picture of the Day</h1><img src="{response.get("url")}" style="max-width:600px"><p>{response.get("explanation")}</p>'
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)