import uuid
from datetime import datetime
from typing import List, Optional
from common.token_manager import get_power_bi_client_from_token
from models.export_models import ExportReportConfiguration, ExportHistory

class ExportRepository:
    def __init__(self):
        # Simulated in-memory stores
        self.export_jobs = {}
        self.export_files = {}
        self.export_history = []

    async def get_export_id(self, user_details, request: ExportReportConfiguration, username: str):
        # 1. File format and mime type selection
        export_type = request.exportType.lower()
        valid_types = {'pdf', 'pptx', 'xlsx', 'csv', 'png'}
        if export_type not in valid_types:
            export_type = 'pdf'
        mime_type = f"application/{export_type}"

        # 2. Simulate asset and permission checks
        # In real code, replace with actual asset lookup and permission logic
        report = {"AssetType": "Report", "CanExport": True, "DatasetId": str(uuid.uuid4()), "ReportParameter": ["param1", "param2"], "AssetName": "Demo Report", "RlsRole": ["role1"], "TenantId": str(uuid.uuid4()), "ReportType": "Regular"}
        dataset = {"RlsRole": ["role2"]}

        if not report or not report["CanExport"]:
            raise Exception("Insufficient access")

        # 3. Simulate tenant and PowerBI client
        tenant_details = {"TenantId": str(uuid.uuid4()), "ServicePrincipalProfileId": str(uuid.uuid4())}
        workspace_id = tenant_details["TenantId"]
        report_id = request.reportId
        if not report_id:
            raise Exception("Report ID is required")
        message_constants = {"PAGINATED_REPORT": "PaginatedReport"}
        pbi_client = get_power_bi_client_from_token(report["ReportType"], tenant_details, message_constants)
        # 4. Paginated report logic
        if request.isPaginated:
            # Validate report parameters
            if request.reportParameter and report["ReportParameter"]:
                invalid_params = [param.name for param in request.reportParameter if param.name not in report["ReportParameter"]]
                if invalid_params:
                    raise Exception(f"Report parameter name(s) {invalid_params} is not valid.")

            # Create export request
            export_request = {
                "format": export_type,
                "reportParameter": request.reportParameter
            }
            # Export Paginated Report using Power BI API
            export_result = await pbi_client.export_report(report_id, workspace_id, export_request)
            if not export_result:
                raise Exception("Failed to export report")

            # Simulate export job creation
            job_id = str(uuid.uuid4())
            self.export_jobs[job_id] = {
                "status": "processing",
                "report_id": str(report_id),
                "export_type": export_type,
                "username": username,
                "created": datetime.utcnow(),
                "file_url": None
            }
            # Simulate export completion
            self.export_jobs[job_id]["status"] = "completed"
            file_content = f"Exported data for report {report_id} in format {export_type} by {username}"
            self.export_files[job_id] = file_content.encode("utf-8")
            self.export_jobs[job_id]["file_url"] = f"/api/download/{job_id}"

            # Simulate export history
            self.export_history.append(ExportHistory(
                exportId=job_id,
                reportId=report_id,
                tenantId=workspace_id,
                reportName=report["AssetName"],
                fileName=f"export_{job_id}.{export_type}",
                reportPageName=request.pageName,
                visualName=request.visualName,
                bookmarkState=request.bookmarkState,
                exportFormat=export_type,
                createdDate=datetime.utcnow()
            ))
            return {
                "jobId": job_id,
                "status": self.export_jobs[job_id]["status"],
                "fileUrl": self.export_jobs[job_id]["file_url"]
            }
        else:
            # Non-paginated report logic

            # create export request for Power BI Rest API
            export_request = {
                "format": export_type,
                "filter": request.filter,
                "fields": request.fields,
                "bookmarkState": request.bookmarkState,
                "pageName": request.pageName,
                "visualName": request.visualName
            }
            # Export Non-Paginated Report using Power BI API
            export_result = await pbi_client.export_report(report_id, workspace_id, export_request)
            if not export_result:
                raise Exception("Failed to export report")
            print(f"Export result: {export_result}")
            # Simulate export job creation
            job_id = str(uuid.uuid4())
            self.export_jobs[job_id] = {
                "status": "processing",
                "report_id": str(report_id),
                "export_type": export_type,
                "username": username,
                "created": datetime.utcnow(),
                "file_url": None
            }
            # Simulate export completion
            self.export_jobs[job_id]["status"] = "completed"
            file_content = f"Exported data for report {report_id} in format {export_type} by {username}"
            self.export_files[job_id] = file_content.encode("utf-8")
            self.export_jobs[job_id]["file_url"] = f"/api/download/{job_id}"

            # Simulate export history
            self.export_history.append(ExportHistory(
                exportId=job_id,
                reportId=report_id,
                tenantId=workspace_id,
                reportName=report["AssetName"],
                fileName=f"export_{job_id}.{export_type}",
                reportPageName=request.pageName,
                visualName=request.visualName,
                bookmarkState=request.bookmarkState,
                exportFormat=export_type,
                createdDate=datetime.utcnow()
            ))
            
            return {
                "jobId": job_id,
                "status": self.export_jobs[job_id]["status"],
                "fileUrl": self.export_jobs[job_id]["file_url"]
            }
        
