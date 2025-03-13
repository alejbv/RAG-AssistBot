from typing import List, Dict
from pymilvus import AsyncMilvusClient, FieldSchema ,DataType


class Collection:
    def __init__(self,uri:str, token:str, collection_name:str, dimension:int):
        self.client = AsyncMilvusClient(uri=uri,token=token)
        self.collection_name = collection_name
        self.dimension = dimension
        self.index_name = "search_index"
    
    async def initialize_collection(self):
        """Check the collection from the Milvus database. If the collection does not exist, it will be created.

        Returns:
            Collection: The collection object.
        """
        if not self.client.has_collection(self.collection_name):
            try:
                fields = [
                    # Use the documents id as primary key
                        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                        FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=256),
                        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=32768),
                        FieldSchema(name="summary", dtype=DataType.VARCHAR, max_length=16384),
                        FieldSchema(name="organism", dtype=DataType.VARCHAR, max_length=256),
                        FieldSchema(name="state", dtype=DataType.VARCHAR, max_length=256),
                        FieldSchema(name="year", dtype=DataType.INT32),
                        FieldSchema(name="normtype", dtype=DataType.VARCHAR, max_length=256),
                        FieldSchema(name="number", dtype=DataType.INT32),
                        FieldSchema(name="read_count", dtype=DataType.INT32),
                        FieldSchema(name="slug", dtype=DataType.VARCHAR, max_length=256),
                        FieldSchema(name="gazette", dtype=DataType.VARCHAR, max_length=256),
                        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                    ]
                
                schema = self.client.create_schema(fields)
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    # Specify the data schema for the new Collection
                    schema=schema,
                )
                print("Collection created")
                
                # Create new index for the collection
                index_param = {"index_type": "AUTOINDEX", "metric_type": "IP"}
                
                await self.client.create_index(self.collection_name, self.index_name, index_param)
                
            except Exception as e:
                print(f"Error in create_collection: {e}")
         
    async def insert(self, data:List[Dict]):
        """Function to store the file in the database"""
        try:
            await self.client.insert(
                collection_name=self.collection_name,
                records=data,
            )
            print("File Stored")
            
        except Exception as e:
            print(f"Error in insert the data: {e}")
    
    async def search(self, vector_query, limit=20):
        """Search the collection using the vector_query"""
        params = {"metric_type": "IP"}
        res = await self.client.search(
            collection_name=self.collection_name,
            data=vector_query,
            anns_field="embedding",
            limit=limit,
            output_fields=["text"],
            search_params=params,
        )[0]
        
        return res
    
    async def close(self):
        """Close the connection to the client"""
        await self.client.close()
    

