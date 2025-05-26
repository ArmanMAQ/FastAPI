from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ParameterValue(BaseModel):
    # Placeholder for actual parameter structure
    name: str
    value: str

class ExportReportConfiguration(BaseModel):
    reportId: UUID
    exportType: str
    isPaginated: bool
    filter: Optional[str] = None
    fields: Optional[List[str]] = None
    bookmarkState: Optional[str] = None
    pageName: Optional[str] = None
    visualName: Optional[str] = None
    reportParameter: Optional[List[ParameterValue]] = None
    class UserContext(BaseModel):
        userId: Optional[str] = None
        userEmail: Optional[str] = None

    userContext: Optional[UserContext] = None

class ExportedReport(BaseModel):
    reportName: str
    resourceFileExtension: str
    # In FastAPI, file streams are handled differently, so we omit ReportStream here

class ExportStatusRequestParams(BaseModel):
    reportId: UUID
    exportId: str

class BlobDetails(BaseModel):
    storageAccountName: str
    storageAccountUrl: str
    containerName: str

class ExportHistory(BaseModel):
    exportId: str
    reportId: UUID
    tenantId: UUID
    reportName: str
    fileName: str
    reportPageName: Optional[str] = None
    visualName: Optional[str] = None
    bookmarkState: Optional[str] = None
    exportFormat: Optional[str] = None
    createdDate: datetime

class ExportFile(BaseModel):
    exportFileType: str
    exportFileName: str
    conn_str: str