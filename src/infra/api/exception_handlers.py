from fastapi import Request
from fastapi.responses import JSONResponse
from src.core.exceptions import ResourceNotFoundException, BusinessRuleException

async def business_rule_handler(request: Request, exc: BusinessRuleException):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno inesperado no servidor"}
    )