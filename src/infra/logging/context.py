from contextvars import ContextVar

_correlation_id_ctx = ContextVar("correlation_id", default=None)

def set_correlation_id(task_id: str):
    """Define o ID da task para o contexto atual"""
    _correlation_id_ctx.set(task_id)

def get_correlation_id():
    """Recupera o ID da task atual ou retorna 'SYSTEM' se não houver"""
    return _correlation_id_ctx.get() or "SYSTEM"