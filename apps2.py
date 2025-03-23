from flask import Flask, redirect, url_for, session, render_template
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'master1234'  # 실제 배포 시에는 안전한 값으로 변경하세요.

# OAuth 객체 생성 및 카카오 설정 등록
oauth = OAuth(app)
oauth.register(
    name='kakao',
    client_id='496b4e67a868e0ce79848add6c77dbf1',  # 카카오 개발자 사이트에서 발급받은 REST API 키
    client_secret='',  # 필요 시 클라이언트 시크릿 입력, 필요하지 않으면 빈 문자열 사용
    access_token_url='https://kauth.kakao.com/oauth/token',
    authorize_url='https://kauth.kakao.com/oauth/authorize',
    api_base_url='https://kapi.kakao.com/v2/',
    client_kwargs={'scope': 'profile_nickname profile_image'},
)

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/login')
def login():
    # _external=True를 사용하면 전체 URL이 생성됩니다.
    redirect_uri = url_for('authorize', _external=True)
    return oauth.kakao.authorize_redirect(redirect_uri)

# 콜백 URL을 '/auth/kakao/callback'으로 설정
@app.route('/auth/kakao/callback')
def authorize():
    token = oauth.kakao.authorize_access_token()
    resp = oauth.kakao.get('user/me', token=token)
    user_info = resp.json()
    session['user'] = user_info
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 포트 5000번에서 서버 실행
    app.run(debug=True, port=5000)
