from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/Practice_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(150), nullable=False)
    work_format = db.Column(db.String(150), nullable=True)
    url = db.Column(db.String(150), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/parse', methods=['POST'])
def parse():
    data = request.get_json()
    job_title, company, city, work_format = data['jobTitle'], data['company'], data['city'], data['workFormat']
    
    response = requests.get('https://hh.ru/search/vacancy', params={'text': f'{job_title} {company} {city} {work_format}', 'area': '1', 'per_page': 10})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        for item in soup.find_all('div', class_='vacancy-serp-item'):
            time.sleep(1)
            name = item.find('a', class_='bloko-link').text
            company = item.find('div', class_='vacancy-serp-item__meta-info-company').text.strip()
            city = item.find('span', class_='vacancy-serp-item__meta-info').text.strip()
            work_format = item.find('span', class_='vacancy-serp-item__work-schedule').text.strip()
            url = item.find('a', class_='bloko-link')['href']
            
            result = {
                "Вакансия": name,
                "Компания": company,
                "Город": city,
                "Формат работы": work_format,
                "Ссылка": url
            }
            results.append(result)
            
            vacancy = Vacancy(
                name=name,
                company=company,
                city=city,
                work_format=work_format,
                url=url
            )
            db.session.add(vacancy)
        db.session.commit()
        return jsonify(results)
    else:
        return jsonify({'error': f"Ошибка: {response.status_code}"}), response.status_code

@app.route('/vacancies', methods=['GET'])
def get_vacancies():
    job_title = request.args.get('jobTitle', '')
    company = request.args.get('company', '')
    city = request.args.get('city', '')
    work_format = request.args.get('workFormat', '')

    query = Vacancy.query
    if job_title:
        query = query.filter(Vacancy.name.ilike(f'%{job_title}%'))
    if company:
        query = query.filter(Vacancy.company.ilike(f'%{company}%'))
    if city:
        query = query.filter(Vacancy.city.ilike(f'%{city}%'))
    if work_format:
        query = query.filter(Vacancy.work_format.ilike(f'%{work_format}%'))

    results = [
        {
            "Вакансия": vacancy.name,
            "Компания": vacancy.company,
            "Город": vacancy.city,
            "Формат работы": vacancy.work_format,
            "Ссылка": vacancy.url
        } for vacancy in query.all()
    ]
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
