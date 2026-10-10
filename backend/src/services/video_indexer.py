'''
Connector : python and azure video indexer
'''

import os 
import time
import logging
import requests
import yt_dlp
from azure.identity import DefaultAzureCredential


logger = logging.getLogger("video-indexer")


class VideoInderxerService:
    def __init__(self):
        self.account_id = os.getenv("AZURE_VI_ACCOUNT_ID")
        self.location = os.getenv("AZURE_VI_LOCATION")
        self.subscription_id = os.getend("AZURE_VI_SUBSCRIPTION_ID")
        self.resource_group = os.getend("AZURE_VI_RESOURCE_GROUP")
        self.vi_name = os.getend("AZURE_VI_NAME")
        self.credential = DefaultAzureCredential()
        
    def get_access_token(self):
        '''
        generating ARM access token
        '''
        try:
            token_object = self.credential.get_token('https://management.azure.com/.default') 
            return token_object.token
        except Exception as e :
            logging.error(f"Failed to get azure token : {e}")
            raise
  
    def get_account_token(self,arm_access_token):
        '''
        Exchanges the ARM token for video indexer account team
        '''
        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self.vi_name}"
            f"/generateAccessToken?api-version=2024-01-01" 
        )
        
        headers = {"Authorization" : f"Bearder {arm_access_token}"}
        payload = {"permissionType" : "Contributor" , "scope" : "Account"}
        response = requests.post(url,headers=headers,json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to get VI account token : {response.text}")
        return response.json().get("accessToken")

    
    def download_ytb_video(self,url,output_path = "temp_video.mp4"):
        '''
        downloads the ytb vid to a local file
        '''
        logger.info(f"Downloading youtube video : {url}")
        ydl_opts = {
            
            "format" :'best[ext=mp4]',
            "outtmpl" : output_path,
            "quit":True,
            "overwrites":True
            
        }
        
        try :
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            logger.info("donwload complete")
            return output_path
            
        except Exception as e:
            raise Exception(f"Youtube vid download failed : {str(e)}")
        
        # upload vid tp azure vi
        
    def upload_video(self,video_path,video_name):
        arm_token = self.get_access_token()
        vi_token = self.get_access_token(arm_token)

        api_url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"

        parms = {
            "accessToken" : vi_token,
            "name" : video_name,
            "privacy":"Private",
            "indexingPreset":"Default"
        }
        logger.info(f"Uploading file {video_path} to azure ....")
        
        #open the file on binary and  stream it on azure
        with open(video_path,'rb') as video_file:
            files = {'file': video_file}
            response = requests.post(api_url,params =parms,files=files)

            if response.status_code != 200:
                raise Exception(f"Azure upload failed : {response.text}")
    
    
    def wait_for_processing(self,video_id):
        logger.info(f'Waiting for video {video_id}to process')
        while True:
            arm_token = self.get_access_token()
            vi_token = self.get_account_token(arm_token)
            
            url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"
            params = { "accessToken" : vi_token}
            response = requests.get(url,params=params)
            data = response.json()

            state = data.get('state')

        
        
        