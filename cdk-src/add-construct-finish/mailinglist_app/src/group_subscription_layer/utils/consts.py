import os
import logging

SOURCE_EMAIL = os.environ.get("SOURCE_EMAIL")

logger = logging.getLogger()
logger.setLevel(logging.INFO) 

SUBSCRIBERS_TABLE = os.environ.get("SUBSCRIBERS_TABLE")
SCHEDULED_MESSAGES_TABLE = os.environ.get("SCHEDULED_MESSAGES_TABLE_NAME")
SCHEDULED_MESSAGES_BUCKET = os.environ.get("SCHEDULED_MESSAGES_BUCKET_NAME") 