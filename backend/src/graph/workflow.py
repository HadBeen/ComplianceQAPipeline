'''
This modeule defines the DAG: directed acyclic graph that orchestrates the video compliance audit process.
it connect the nodes using the stategraph from langgraph

Start -> index_video_node -> audio_content_node -> END
'''
from langgraph.graph import StateGraph , END
from backend.src.graph.state import VideoAuditState
from backend.src.graph.nodes import (
    index_video_node,
    audio_content_node
    )

def create_graph():
    '''
    Constructs and compiles the Langgraph workflow
    returns :
    Compiles graph : runnable object for execution
    '''
    
    # initialize the graph with state schema
    workflow = StateGraph(state_schema=VideoAuditState)
    #add the nodes
    workflow.add_node("indexer",index_video_node)
    workflow.add_node("auditor",audio_content_node)
    #define the entry point 
    workflow.set_entry_point("indexer")
    #define the edges
    workflow.add_edge("indexer","auditor")
    # once the audit if complete the workflow ends
    workflow.add_edge("auditor",END)
    
    # compile the graph 
    app = workflow.compile()
    
    return app


app = create_graph()
    


