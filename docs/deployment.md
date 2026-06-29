# Deployment Guide

MAVVE is designed to scale horizontally to handle thousands of concurrent conversational sessions.

## 🐳 Docker Deployment (Recommended)

The easiest way to deploy MAVVE is using the provided `docker-compose.yml`.

```bash
# 1. Configure environment variables
cp backend/.env.example backend/.env

# 2. Build and run in detached mode
docker-compose up -d --build
```

### Environment Variables for Production
When deploying to production, ensure the following variables are strictly secured:
- `DATABASE_URL`: Ensure your PostgreSQL instance is not publicly accessible.
- `REDIS_URL`: Use Redis authentication in production.
- `WHATSAPP_API_TOKEN`: Keep your Meta long-lived access token secure.
- `GEMINI_API_KEY`: Google AI Studio Key.
- `BHASHINI_MOCK_MODE`: Set to `false` in production to hit real APIs.

## ☁️ Cloud Deployment Architecture (AWS)

For enterprise scale (handling 10k+ concurrent WhatsApp chats), we recommend the following AWS Architecture:

1. **Load Balancing**: AWS Application Load Balancer (ALB) to route incoming WhatsApp webhooks to the FastAPI backend.
2. **Compute**: Amazon EKS (Elastic Kubernetes Service) running horizontally scaled FastAPI pods.
3. **State Management**: Amazon ElastiCache (Redis) to manage LangGraph session states efficiently across multiple pods.
4. **Database**: Amazon RDS (PostgreSQL) for persistent storage of Orders and Transcripts.

### Scaling Considerations
- **Stateless Backend**: The FastAPI backend is completely stateless. All session data is stored in Redis. You can autoscale pods based on CPU/Memory without losing conversation context.
- **Background Tasks**: Currently, webhook processing is handled via FastAPI `BackgroundTasks`. For production scale, it is highly recommended to offload webhook processing to **Celery + RabbitMQ/Redis** to prevent dropping messages under heavy webhook load.

## 📊 Monitoring & Alerting

- **Prometheus/Grafana**: Export FastAPI metrics to monitor average response latency and LLM generation times.
- **Sentry**: Integrate Sentry to catch exceptions in the LangGraph execution flow.
- **WhatsApp API Limits**: Monitor Meta's rate limits (Tier 1 vs Tier 4) to ensure you have enough throughput for outgoing messages.
