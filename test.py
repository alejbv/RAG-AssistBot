from pymilvus import connections
from utils import load_config

config = load_config()
connections.connect(
    uri=config["MILVUS_URI"],
    token=config["MILVUS_API_KEY"]
)