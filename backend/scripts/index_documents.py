import os
import glob
import logging
from dotenv import load_dotenv
from openai import vector_stores
from streamlit import form

load_dotenv(override=True)

#doc loaders and spliters
from langchain_community.document_loaders import  PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# azure components import
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch 


# set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger("indexer")

def index_docx():
    '''
    Reads pdfs ,chunks them then uploads them to azure ai search
    '''
    
    #define paths , we look for data folders
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir,"../../backend/data")
    
    # check data env
    logger.info("=="*60)
    logger.info("Envirement configuration check: ")
    logger.info(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    logger.info(f"AZURE_OPENAI_API_VERSION: {os.getenv('AZURE_OPENAI_API_VERSION')}")
    logger.info(f"Embedding deployment: {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT','text-embedding-3-small')}")
    logger.info(f"AZURE_SEARCH_ENDPOINT: {os.getenv('AZURE_SEARCH_ENDPOINT')}")
    logger.info(f"AZURE_SEARCH_INDEX_NAME: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
    logger.info("=="*60)
    
    #validate the required env vars
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_API_KEY",
        "AZURE_SEARCH_INDEX_NAME"
    ]
    
    missings_vars = [var for var in vars if not os.getenv(var)]
    if missings_vars:
        logger.error(f'missing required env variable : {missings_vars}')
        logger.error('check your env file')
        
    # initialize the embedding model : turning text into vectors
    try : 
        logger.info("Initializing Azure Open AI Embeddings.....")
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment= os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT','text-embedding-3-small'),
            azure_endpoint= os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            openai_api_version=os.getenv('AZURE_OPENAI_API_VERSION')
        )
        
        logger.infor("Embedding model initialized succesfully")
        
    except Exception as e:
        logger.error(f'Failed to initialize embedding : {e}')
        logger.error("Verify your azure OPEN AI deployement name and endpoint")
        return
        
    # initialize the azure search
    try : 
        logger.info("Initializing Azure AI Search Embeddings.....")
        embeddings = AzureOpenAIEmbeddings(
            azure_search_endpoint= os.getenv('AZURE_SEARCH_ENDPOINT'),
            azure_search_key= os.getenv('AZURE_SEARCH_API_KEY'),
            index_name=os.getenv('AZURE_SEARCH_INDEX_NAME'),
            embedding_function=embeddings.embed_query
        )
        
        logger.infor("vector store initialized succesfully")
        
    except Exception as e:
        logger.error(f'Failed to initialize Azure search: {e}')
        logger.error("Verify your azure searcht")
        return
    
    #find pdf files
    pdf_files = glob.glob(os.path.join(data_folder,"*.pdf"))
    if not pdf_files:
        logger.warning(f'No pdfs found in {data_folder}')
    
    logger.info(f'found {len(pdf_files)} pfds to process : {[os.path.basename(f) for f in pdf_files]}')
    all_splits = []


    for pdf_file in pdf_files :
        try :
            logger.info(f'Loading:{os.path.basename(pdf_file)}.....')
            loader = PyPDFLoader(pdf_file)
            raw_docs = loader.load()
            
            # chunking stratigy
            
            text_spliter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap=200
            )
            splits = text_spliter.split_documents(raw_docs)
            for split in splits:
                split.metadata['source'] = os.path.basename(pdf_file)
            
            all_splits.extend(splits)
            logger.info(f"split into {len(splits)} chunks")
        except Exception as e :
            logger.error(f"Fail to process {pdf_file} : {e}")
            
        
        # upload to azure 
        if all_splits:
            logger.info(f"uploading {len(all_splits)} chunks to azure AI search index")
            try:
                
                vector_stores.add_documents(documents = all_splits)
                logger.info('='*60)
                logger.info("Indexing complete knowledge base is ready...")
                logger.info(f"total chuncks indexed : {len(all_splits)}")
                logger.info('='*60)
                
            except Exception as e:
                logger.error(f'Failed to upload the docs : {e}')
                logger.error("check Azure search config ")
        else :
            logger.warning("No docs were processed")


if __name__ == '__main__':
    index_docx()
                
        
    