import os
import random
import requests
from flask import Flask, render_template, request, flash
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
SITE_KEY_CAPTCHA = os.getenv('SITE_KEY_CAPTCHA')
SECRET_KEY_CAPTCHA = os.getenv('SECRET_KEY_CAPTCHA')
VERIFY_URL = os.getenv('VERIFY_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
options = [
    {'title': 'Главная страница', 'url': '/'},
    {'title': 'Получить картинку', 'url': 'get-picture'},
    {'title': 'Обратная связь', 'url': 'feedback'}
]


@app.route('/')
def index():
    return render_template('index.html', title="Главная", menu=options)


@app.route('/get-picture', methods=['POST', 'GET'])
def get_picture():
    picture_url = ''
    if request.method == "POST":
        secret_response = request.form['g-recaptcha-response']
        verify_response = requests.post(url=f'{VERIFY_URL}?secret={SECRET_KEY_CAPTCHA}&response={secret_response}').json()
        # print(verify_response['success'], verify_response['score'])
        if not verify_response['success'] or verify_response['score'] < 0.5:
            return render_template('get-picture.html', title='Получить картинку', menu=options, picture_url=picture_url,
                                   site_key=SITE_KEY_CAPTCHA)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(f'https://unsplash.com/napi/search/photos?query=cat&per_page=20&page=1&xp',
                                headers=headers).json()
        page_num = random.randint(0, response['total_pages'])
        pic_num = random.randint(0, 20)
        response = requests.get(f'https://unsplash.com/napi/search/photos?query=cat&per_page=20&page={page_num}&xp',
                                headers=headers).json()
        picture_url = response['results'][pic_num]['urls']['raw']
    return render_template('get-picture.html', title='Получить картинку', menu=options, picture_url=picture_url,
                           site_key=SITE_KEY_CAPTCHA)


@app.route('/feedback', methods=['POST', 'GET'])
def feedback():
    if request.method == "POST":
        if len(request.form['text']) > 4:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Сообщение не было отправлено: длина должна быть > 4!', category='danger')
    return render_template('feedback.html', title="Обратная связь", menu=options)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Такой страницы нет :(', menu=options)


if __name__ == '__main__':
    app.run(debug=False)
