import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os
import uuid
from threading import Lock
import io


from helper import export_data_route
# from models.export_models import ExportReportConfiguration, ExportFile
# from repositories.export_repository import ExportRepository
# from common.token_manager import get_power_bi_client_from_token
# from api.v1.endpoints.export import router as export_router


# Define the request body model
class ExportRequestBody(BaseModel):
    exportFileType: str
    exportFileName: str
    conn_str: str
    report_subscription: dict | None = None # Made optional, adjust if always required


app = FastAPI()
# repo = ExportRepository()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration from appsettings.json
config_path = os.path.join(os.path.dirname(__file__), 'appsettings.json')
if os.path.exists(config_path):
    with open(config_path) as f:
        APPSETTINGS = json.load(f)
else:
    APPSETTINGS = {}

export_jobs = {}
export_files = {}
export_lock = Lock()

# app.include_router(export_router, prefix="/api/v1")

@app.get("/")
def home():
    return {"message": "Welcome to the migrated Python FastAPI2!"}
@app.get("/api/Test")
async def api_test():
    return JSONResponse(content={"message": "Test API is working!"})

@app.put("/api/exportFile")
async def export_data(payload: ExportRequestBody):
    # Access data from the Pydantic model
    exportFileType = payload.exportFileType
    exportFileName = payload.exportFileName
    conn_str = payload.conn_str
    report_subscription = payload.report_subscription

    if not exportFileType or not exportFileName:
        raise HTTPException(status_code=400, detail="Missing export file type or name")
    
    if not conn_str:
        raise HTTPException(status_code=400, detail="Missing connection string")
   
    job_id = str(uuid.uuid4())
    req = {
        "job_id": job_id,
        "file_type": exportFileType,
        "conn_str": conn_str,
        "filename_base": exportFileName,
        "report_subscription": report_subscription, # Use the value from the payload
    }
 
    # Call repository method to export data
    # Assuming export_data_route is synchronous. If it's async, 'await' it.
    # If it's long-running and should be in the background, you'd use BackgroundTasks.
    response_data = export_data_route(req)
    
    # You might want to return more details from export_data_route
    # For now, keeping the original response structure
    return JSONResponse(content={"job_id": job_id, "status": "In progress", "message": "Export job started", "details": response_data})

# @app.get("/api/status/{job_id}")
# def api_status(job_id: str):
#     with export_lock:
#         job = export_jobs.get(job_id)
#     if not job:
#         raise HTTPException(status_code=404, detail="Job not found")
#     resp = {"status": job['status']}
#     if job['status'] == 'completed':
#         resp['fileUrl'] = job['file_url']
#     return JSONResponse(content=resp)

# @app.get("/api/download/{job_id}")
# def api_download(job_id: str):
#     with export_lock:
#         file_content = export_files.get(job_id)
#     if not file_content:
#         raise HTTPException(status_code=404, detail="File not found or not ready")
#     return StreamingResponse(
#         io.BytesIO(file_content),
#         media_type='text/csv',
#         headers={
#             'Content-Disposition': f'attachment; filename="export_{job_id}.csv"'
#         }
#     )

@app.get("/health")
def health():
    return {"status": "Healthy"}

# @app.post("/api/pbi-export")
# async def pbi_export(
#     request: ExportReportConfiguration,
#     authorization: str = Header(None, description="JWT access token as 'Bearer <token>'")
# ):
#     """
#     Accepts a JWT Bearer token from the Authorization header and uses it to create a PowerBIClient for API calls.
#     """
#     if not authorization or not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Missing or invalid Authorization header. Please provide 'Bearer <token>' in the Authorization header.")
#     token = authorization.split(" ", 1)[1]
#     pbi_client = get_power_bi_client_from_token(token)
#     # Example usage: (You can expand this to call export_report, etc.)
#     # group_id = ...
#     # report_id = ...
#     # export_body = {...}
#     # result = pbi_client.export_report(group_id, report_id, export_body)
#     return {"message": "Power BI client created with provided JWT access token."}