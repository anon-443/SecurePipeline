import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_ENVIRONMENT = os.getenv("APP_ENVIRONMENT", "development")

app = Flask(__name__)
REQUEST_COUNTER = Counter(
    "securepipeline_http_requests_total",
    "Total HTTP requests handled by SecurePipeline",
    ["endpoint", "method", "status"],
)


def response(payload: dict, status: int = 200):
    REQUEST_COUNTER.labels(request.endpoint or "unknown", request.method, status).inc()
    return jsonify(payload), status


@app.get("/")
def index():
    return response(
        {
            "service": "SecurePipeline",
            "message": "DevSecOps deployment platform is running",
            "version": APP_VERSION,
            "environment": APP_ENVIRONMENT,
        }
    )


@app.get("/health")
def health():
    return response({"status": "healthy", "service": "securepipeline"})


@app.get("/ready")
def ready():
    return response({"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()})


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.errorhandler(404)
def not_found(_error):
    return response({"error": "resource not found"}, 404)


@app.errorhandler(500)
def internal_error(_error):
    return response({"error": "internal server error"}, 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
