import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify, session
from flask_cors import CORS
from models.user import db
from routes.user import user_bp
from routes.file_browser import file_browser_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT' # 数据加密签名

# 启用CORS
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(file_browser_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    ip = data.get('ip')
    port = data.get('port')
    username = data.get('username')
    password = data.get('password')
    # 这里可以添加实际的连接验证逻辑
    if ip and port and username and password:
        # 假设验证通过
        session['logged_in'] = True
        session['ip'] = ip
        session['port'] = port
        session['username'] = username
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'msg': '信息不完整'}), 400


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    # 未登录时，始终返回login.html
    if not session.get('logged_in'):
        return send_from_directory(static_folder_path, 'login.html')

    # 已登录，正常访问静态资源
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
