# app/__init__.py
from flask import Flask, request, jsonify
import os
from pathlib import Path
from .config import DevConfig, ProdConfig
from .extensions import migrate

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    # 1) 환경 설정 로드 (production / dev)
    if os.getenv("FLASK_ENV") == "production":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)

    # 2) DB URI 확정 (환경변수 없으면 instance/summary.db 사용)
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        sqlite_path = Path(app.instance_path) / "summary.db"
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path.as_posix()}"

    # 3) 엔진 옵션 & SQLAlchemy 기본 설정
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {"pool_pre_ping": True})
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # 4) DB init & 테이블 생성
    from .models import db  # db = SQLAlchemy()
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        from .models import News, NewsSummary  # 모델 import 후
        db.create_all()

    # 5) 블루프린트 등록 (※ summary_route.py 가 맞는 파일명인지 확인!)
    from .routes.summary_route import summary_bp
    app.register_blueprint(summary_bp)  # summary_bp에 url_prefix가 이미 있다면 이대로

    # 6) 헬스체크
    @app.get("/")
    def health():
        return {"ok": True}

    # 7) 라우트 목록/요청 로깅 (디버그용)
    @app.get("/__routes")
    def __routes():
        return {
            "db_uri": app.config.get("SQLALCHEMY_DATABASE_URI"),
            "routes": [
                {"rule": r.rule, "methods": sorted(list(r.methods))}
                for r in app.url_map.iter_rules()
            ],
        }

    @app.before_request
    def _log_req():
        print(">>", request.method, request.path, request.headers.get("Content-Type"))

    # 8) 404 디버그 보조 (요청 경로가 /summary* 인데 404면 라우트 출력)
    @app.errorhandler(404)
    def _not_found(e):
        if request.path.startswith("/summary"):
            return jsonify({
                "error": "Not Found",
                "path": request.path,
                "hint": "아래 routes에서 /summary 엔드포인트가 있는지 확인하세요.",
                "routes": [r.rule for r in app.url_map.iter_rules()]
            }), 404
        return e, 404

    # 9) 부팅 시 DB/인스턴스 경로 한번 찍어두면 혼동 없음
    print("[BOOT] instance_path:", app.instance_path)
    print("[BOOT] SQLALCHEMY_DATABASE_URI:", app.config["SQLALCHEMY_DATABASE_URI"])

    return app
