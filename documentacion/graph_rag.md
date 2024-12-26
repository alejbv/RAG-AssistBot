## Pasos para construir un Knowledge Graph
1. Entity Extraction and Linking. 

         The foundation of a good knowledge graph lies in accurate entity extraction and linking. I’ve found that using a combination of named entity recognition (NER) models and entity linking techniques yields the best results. For instance, you might use spaCy for initial NER and then employ a more sophisticated entity linking model like BLINK to resolve ambiguities and link entities to a knowledge base like Wikidata.

2.  Relationship Extraction 
        
        Identifying relationships between entities is where knowledge graphs truly shine. I’ve had success using distant supervision techniques combined with pre-trained language models fine-tuned on domain-specific data. This approach allows for the extraction of both explicit and implicit relationships, creating a more comprehensive graph structure.

3. Attribute Enrichment 

        To make your knowledge graph more informative, enrich entities with relevant attributes. This could involve integrating data from multiple sources, such as combining structured database information with unstructured text extracted from documents.

4. Ontology Design

         Designing a well-structured ontology is critical for organizing your knowledge graph. I recommend starting with existing ontologies like Schema.org or domain-specific ones, and then extending them to fit your specific use case.
## Pasos del GraphRAG  para procesar una Query

1. Keyword extraction using an LLM.
    
       Identify key entities or keywords essential for linking to relevant nodes within the Knowledge Graph. To enhance entity extraction, the query is also embedded as a vector, enabling a vector search to identify nodes in the Knowledge Graph that are most similar to the query. To ensure comprehensive coverage of relevant entities, a Top-N retrieval approach is employed, capturing a set of the most relevant entities from the Knowledge Graph to minimize the risk of missing critical information.


2. A vector search on the knowledge graph to identify relevant nodes and relationships.

        Once the keywords and entities are identified, Paths Extraction finds the connections between these entities in the Knowledge Graph. The system is using Neo4J to search for entities either:

        1. The Shortest Paths between matched entities (for cases with sufficient keywords and entities).
        
        2. The Hop-1, nearest neighbours, of those entities when fewer keywords or entities are identified.

        These paths capture the relationships and context that are important to answering the user’s query, connecting entities with relevant information across the knowledge graph. These strategies allow for capturing both direct and contextual relationships between entities, enhancing the knowledge graph’s capacity to answer the user’s query effectively.


3. Organizing nodes and entitys:
        
        Path re-ordering serves a critical function by restructuring paths in cases where context length must be limited due to LLM constraints. By prioritizing the most relevant paths first, this step partially addresses the limited context length as well as the “lost-in-the-middle” issue, ensuring that key information is positioned at the beginning and thus maximizing the LLM’s response quality. Paths are ordered strictly in descending order of relevance scores (a combination of similarity to the query and inverse TF-IDF and based on relations preferences), but this ordering alone does not fully address the “lost-in-the-middle” problem.

4. Graph to text:
        
        In this step, structured relationships and entities from the graph are converted into text sequences. The Graph-To-Text component transforms the graph’s structured data into human-readable text that can be processed by the LLM. All relationships are formatted as triplets and regrouped when necessary by node names. This conversion allows the LLM to incorporate the explicit knowledge contained in the graph as part of its reasoning process.

5. These retrieved relationships are then used to enrich the LLM’s context, enabling it to generate a more informed response.

        Finally, the enriched context, together with the original query, is fed into the LLM for answer generation. Prompt Engineering is critical here, as the structure of the prompt can significantly impact the coherence and accuracy of the response

```python
#Example of a Prompt Template
prompt_template = """
You are a virtual assistant designed to assist biomedical professionals by providing precise and relevant answers to their inquiries.
Base your answers solely on the relationships and entities provided in the context enclosed by ####. Do not use outside knowledge or assumptions.

### Guidelines:
1. Identify Key Entities and Relationships:
- Find entities mentioned in the question within the context.
2. Trace Relevant Paths:
- Follow logical paths connecting these entities through the given relationships.
3. Extract Relevant Information:
- Extract entities and relationships directly relevant to the question.
.....
### Example 1:
**Question 1:**
"I am studying types of anemia. What are some specific types of anemia?"
**Context:**
anemia -> parent-child -> (iron-deficiency anemia, hemolytic anemia, sickle-cell anemia, aplastic anemia)
breast cancer -> associated_with -> (DKK1, SLC6A3, ESR2)
**Answer:**
['iron-deficiency anemia', 'hemolytic anemia', 'sickle-cell anemia', 'aplastic anemia']
**Question:**
{question}
**Context:**
####
{context}
####
"""
```
