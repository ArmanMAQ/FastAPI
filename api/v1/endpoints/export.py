# Export endpoints for API v1
from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.responses import JSONResponse, StreamingResponse
import io
import uuid
from models.export_models import ExportReportConfiguration
from repositories.export_repository import ExportRepository
from common.token_manager import get_power_bi_client_from_token

router = APIRouter(prefix="/export", tags=["Export"])
repo = ExportRepository()

@router.post("")
async def create_export(request: ExportReportConfiguration):
    user_id = request.userContext.get('userId') if request.userContext and isinstance(request.userContext, dict) else str(uuid.uuid4())
    username = request.userContext.get('email') if request.userContext and isinstance(request.userContext, dict) else 'unknown'
    result = await repo.get_export_id(user_id, request, username)
    return JSONResponse(content=result)

@router.get("/status/{job_id}")
async def get_export_status(job_id: str):
    # In a real implementation, use repo.get_status
    # Here, simulate with in-memory jobs if needed
    raise HTTPException(status_code=501, detail="Not implemented. Use main app endpoints or implement repo.get_status.")

@router.get("/download/{job_id}")
async def download_export(job_id: str):
    # In a real implementation, use repo.get_exported_report
    # Here, simulate with in-memory files if needed
    raise HTTPException(status_code=501, detail="Not implemented. Use main app endpoints or implement repo.get_exported_report.")

@router.post("/pbi")
async def export_with_pbi(
    request: ExportReportConfiguration,
    authorization: str = Header(None, description="JWT access token as 'Bearer <token>'")
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header. Please provide 'Bearer <token>' in the Authorization header.")
    token = authorization.split(" ", 1)[1]
    pbi_client = get_power_bi_client_from_token(token)
    # Example: Use pbi_client to call Power BI REST API
    return {"message": "Power BI client created with provided JWT access token."}
