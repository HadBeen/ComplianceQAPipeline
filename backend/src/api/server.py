#fastapi

import uuid
import logging
from fastapi import FastAPI,HTTPException

from pydantic import BaseModel
from typing import List,Optional

#load env vars
from dotenv import load_dotenv
load_dotenv(override=True)

# initialize telemetry
from backend.src.api.telemetry import setup_telemetry
setup_telemetry()

# import workflow
from backend.src.graph.workflow import app as compliance_app

# configure logger
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("api-server")


# create fastapi app
app = FastAPI(
    title= "Brand gardian AI API",
    description="API for auditing video content against brand compliance rules.",
    version="1.0.0"

)

#define data models

class AuditRequest(BaseModel):
    '''
    invalid : 422 error
    {"videdo_url":1236}
    
    '''
    video_url : str

class ComplianceIssue(BaseModel):
    category : str
    severity : str
    description : str 
    
class AuditResponse(BaseModel):
    session_id : str
    video_id : str
    status : str
    final_report : str
    compliance_results : List[ComplianceIssue]


#define the main endpoint
@app.post("/audit",response_model=AuditResponse)


async def audit_video(request:AuditRequest):
    ''' main api endpoint that triggers the complinace audit workflow'''

    
    session_id = str(uuid.uuid4())
    video_id_short = f"vid_{session_id[:8]}"
    logger.info(f"Recieved the audit request: {request.video_url} (session : {session_id})")
    #graph input 
    
    initial_inputs = {
        "video_url" : request.video_url ,
        "video_id" :video_id_short ,
        "compliance_results" : [] ,
        "errors" : []
        
    }
    
    try:
        final_state = compliance_app.invoke(initial_inputs)
        return AuditResponse(
            session_id=session_id,
            video_id=final_state.get("video_id"),
            status = final_state.get("final_status","UNKNOWN"),
            final_report= final_state.get("final_report","No report generated"),
            compliance_results=final_state.get("compliance_results",[])
            
        )
    
    except Exception as e:
        logger.error(f"Audit failed : {e}")
        raise HTTPException(
            status_code=500,
            detail=f"workflow execution failed : {str(e)}"
        )
    
@app.get("/health")

def health_check():
    '''enfpoint to check if api works or not'''

    return {"status":"Healthy","service":"brand guardian AI"}
    

