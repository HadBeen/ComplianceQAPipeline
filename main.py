'''
main execution entry 
'''

import uuid 
import json
import logging
from pprint import pprint

from dotenv import load_dotenv
load_dotenv(override=True)

from backend.src.graph.workflow import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s -%(name)s -%(levelname)s -%(message)s'
)

logger = logging.getLogger("brand-guardian-runner")


def run_cli_simulation():
    '''Simulate the video compliance qudit request'''

    #generate session id
    print("ok")
    session_id= str(uuid.uuid4())
    logging.info(f'starting audit session : {session_id}')

    # define the initial state
    initial_inputs = {
        # "video_url":"https://youtu.be/tFDn4l0PpR4",
        "video_url":"https://youtu.be/xGhIVEyxayg",
        "video_id":f"vid_{session_id[:8]}",
        "compliance_results":[],
        "errors": []

    }
    print('----initialize workflow-----')
    print(f"Input Payload : {json.dumps(initial_inputs,indent=2)}")

    try:
        final_state = app.invoke(initial_inputs)
        print("------ Workflow execution is complete ------")
        
        
        print("\n Compliance Audit repport")
        print(f"video id : {final_state.get('video_id')}")
        print(f"status : {final_state.get('final_status')}")

        print("\n [VIOLATION DETECTED]")
        
        results = final_state.get('compliance_results',[])
        if results:
            for issue in results:
                print(f"-[{issue.get('severity')}] [{issue.get('category')}] : [{issue.get('description')}]")
        
        else:
            print("No violations detected")        

        print('\n [FINAL SUMMARY]')
        print(final_state.get('final_report'))

    except Exception as e:
        logger.error(f"Workflow execution failed : {e}")

        raise e

if __name__ == "__main__":
    run_cli_simulation()
    
        

        
    

