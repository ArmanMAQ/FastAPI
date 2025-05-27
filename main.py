import uvicorn
from fastapi import FastAPI,Query, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
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
    return {"message": "Welcome to the migrated Python FastAPI3!"}
@app.get("/api/Test")
async def api_test():
    return JSONResponse(content={"message": "Test API is working!"})

@app.post("/api/exportFile")
async def api_exportFile(
    exportFileType: str = Query(..., description="Type of export file"),
    exportFileName: str = Query(..., description="Base name of the export file"),
    conn_str: str = Query(..., description="Connection string to the data source")
):
    req = {
        "file_type": exportFileType,
        "conn_str": conn_str,
        "filename_base": exportFileName,
    }
    res = export_data_route(req)

    message = res.get("message", "Export job started")
    execution_time = str(res.get("execution_time", "Unknown")) + " seconds"
    file_path = res.get("filepath")

    job_id = str(uuid.uuid4())
    export_jobs[job_id] = {
        "status": "in_progress",
        "exportFileType": exportFileType,
        "exportFileName": exportFileName
    }

    return JSONResponse(content={
        "job_id": job_id,
        "message": message,
        "execution_time": execution_time,
        "file_path": file_path
    })

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