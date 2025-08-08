from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import News, NewsSummary
from ..prompt_manager import PromptManager
from ..services.summarizer import summarize

summary_bp = Blueprint("summary", __name__, url_prefix="/summary")

@summary_bp.route("/", methods=["POST"])    # 슬래그 혼동 방지
@summary_bp.route("", methods=["POST"])
def create_summary():
    data = request.get_json(force=True)
    text = data.get("text")
    news_id = data.get("news_id")
    type_ = (data.get("type") or "AIBOT").upper()
    prompt = PromptManager.get(data.get("prompt"), type_)

    if not text and not news_id:
        return jsonify({"error": "text 또는 news_id가 필요합니다."}), 400

    if not text:
        news = News.query.get(news_id)
        if not news:
            return jsonify({"error": "뉴스가 없습니다."}), 404
        text = news.content

    if news_id:
        cached = NewsSummary.query.filter_by(news_id=news_id, type=type_).first()
        if cached:
            return jsonify({"summary": cached.summary_text, "cached": True})

    summary_text = summarize(text, prompt)
    ns = NewsSummary(news_id=news_id, type=type_, summary_text=summary_text)
    db.session.add(ns); db.session.commit()

    return jsonify({"summary": summary_text, "cached": False}), 201
