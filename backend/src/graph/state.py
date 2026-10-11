import operator
from typing import Annotated,List, Dict,Optional,Any,TypedDict 


#error report structure 
class ComplianceIssue(TypedDict):
    category: str
    description: str
    severity: str
    timestamp: Optional[str]


#defines the state that pass through the agentic workflow

class VideoAuditState(TypedDict):
    '''State for the video audit workflow'''
    
    #inputs
    video_url: str
    video_id: str
    
    # ingestion and extraction of data
    local_file_path: Optional[str]
    video_metadata: Dict[str, Any]
    transcript: Optional[str] #speech to text
    ocr_text: List[str]


    #analysis output
    compliance_results: Annotated[List[ComplianceIssue],operator.add]
    
    # deliverable
    final_status : str #Pass | Fail
    final_repport : str #markdown
    
    #system observability 
    #errors 
    errors : Annotated[List[str],operator.add]