import logging
import watchtower
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger
from src.infra.logging.context import get_correlation_id

class CorrelationIdFilter(logging.Filter):
    """Filtro que injeta o task_id em todo registro de log"""
    def filter(self, record):
        record.task_id = get_correlation_id()
        return True

def setup_logging(app_name="video-ingest", region="us-west-2"):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 1. Filtro de Contexto (Injeta o task_id)
    correlation_filter = CorrelationIdFilter()

    # 2. Formatter JSON (Para o CloudWatch entender os campos)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(task_id)s'
    )

    # 3. Handler do CloudWatch
    try:
        cw_handler = watchtower.CloudWatchLogHandler(
            log_group=app_name,
            stream_name=f"app-{datetime.now().strftime('%Y-%m-%d')}",
            boto3_session=None, # Usa as credenciais padrão do ambiente (boto3)
            create_log_group=True
        )
        cw_handler.setFormatter(formatter)
        cw_handler.addFilter(correlation_filter)
        logger.addHandler(cw_handler)
    except Exception as e:
        print(f"Aviso: Não foi possível conectar ao CloudWatch: {e}")

    # 4. Handler de Console (Para ver logs locais)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(correlation_filter)
    logger.addHandler(console_handler)

    logging.info("Sistema de Logging Inicializado com CloudWatch")