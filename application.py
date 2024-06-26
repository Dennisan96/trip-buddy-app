from flask import Flask, request, jsonify
import logging
import os 
from dotenv import load_dotenv
from aws_utils import is_on_beanstalk


# make log files
LOG_DIRECTORY = "/var/app/current/log"
if is_on_beanstalk() and not os.path.exists(LOG_DIRECTORY):
    print("On beanstalk env")
    os.makedirs(LOG_DIRECTORY)
    logging.basicConfig(filename='/var/app/current/log/app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
else:
    print("Not on beanstalk")
    load_dotenv()

from app.app import app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.debug = True    
    app.run(port=8000)