# azure opentelemetry integration

import os
import logging
from azure.monitor.opentelemetry import configure_azure_monitor


logger = logging.getLogger('brand-gard-telemetry')

def setup_telemetry():
    '''
    azure monitor opentelemetry
    tracks , http requests, database,errors
    
    auto capture all api requests
    no need to log endpoints
    '''
    
    #retrieve connection string
    connection_string = os.getenv("APPLICATION_CONNECTION_STRING")

    # check if it's configured
    if not connection_string:
        logger.warning("No instrumentation key found .Telementary is DISABLED")
    
    try:
        configure_azure_monitor(
            connection_string=connection_string,
            logger_name = "brand-gardian-tracer"
        )
    
        logger.info("Azure monitor tracking enabled and connected")
    except Exception as e:
        logger.error(f"Failed to initialize Azure monitor: {e}")
    