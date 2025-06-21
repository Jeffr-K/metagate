from fastapi import Request
from fastapi.responses import Response as FastAPIResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from .config import prometheus_config

# HTTP 요청 메트릭
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=prometheus_config.request_duration_buckets,
)

http_request_size_bytes = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
    buckets=prometheus_config.request_size_buckets,
)

# 데이터베이스 메트릭
db_connections_active = Gauge(
    "db_connections_active", "Number of active database connections"
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds", "Database query duration in seconds", ["operation"]
)

# Redis 메트릭
redis_operations_total = Counter(
    "redis_operations_total",
    "Total number of Redis operations",
    ["operation", "status"],
)

redis_operation_duration_seconds = Histogram(
    "redis_operation_duration_seconds",
    "Redis operation duration in seconds",
    ["operation"],
)


def get_metrics():
    """Prometheus 메트릭 반환"""
    return FastAPIResponse(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


async def metrics_middleware(request: Request, call_next):
    """메트릭 수집 미들웨어"""
    import time

    start_time = time.time()

    # 요청 크기 측정
    content_length = request.headers.get("content-length")
    if content_length:
        http_request_size_bytes.labels(
            method=request.method, endpoint=request.url.path
        ).observe(float(content_length))

    # 응답 처리
    response = await call_next(request)

    # 지속 시간 측정
    duration = time.time() - start_time
    http_request_duration_seconds.labels(
        method=request.method, endpoint=request.url.path
    ).observe(duration)

    # 요청 수 증가
    http_requests_total.labels(
        method=request.method, endpoint=request.url.path, status=response.status_code
    ).inc()

    return response
