from fastapi import FastAPI
from dotenv import load_dotenv
from src.infra.api.routers import routes
from src.infra.api.exception_handlers import (
    resource_not_found_handler, 
    business_rule_handler, 
    general_exception_handler
)

load_dotenv()

app = FastAPI(title="Video Ingest API")

app.add_exception_handler(ResourceNotFoundException, resource_not_found_handler)
app.add_exception_handler(BusinessRuleException, business_rule_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(routes.router, prefix="/api/v1")