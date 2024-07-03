from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from flask_sqlalchemy import SQLAlchemy

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
    
    params = {
        'text': f'{job_title} {company} {city} {work_format}',
        'area': '1',
        'per_page': 10
    }

    response = requests.get('https://api.hh.ru/vacancies', params=params)
    if response.status_code == 200:
        data = response.json()
        results = []

        for item in data['items']:
            name = item['name']
            company = item['employer']['name']
            city = item['area']['name']
            work_format = item.get('schedule', {}).get('name', '')
            url = item['alternate_url']
            
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
    query_params = {key: request.args.get(key, '') for key in ['jobTitle', 'company', 'city', 'workFormat']}
    query = Vacancy.query

    for key, value in query_params.items():
        if value:
            query = query.filter(getattr(Vacancy, key).ilike(f'%{value}%'))

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

