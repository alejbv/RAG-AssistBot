# Cómo funciona el RAG tradicional
Un flujo de trabajo típico de RAG suele contener varios pasos de procesamiento intermedios: 

**Clasificación de consultas**: determinar si la recuperación es necesaria para una consulta de entrada determinada

**Recuperación**: obtener de forma eficiente los documentos relevantes para la consulta 

**Reclasificación**:refinar el orden de los documentos recuperados en función de su relevancia para la consulta 

**Reempaquetado**:organizar los documentos recuperados en uno estructurado para una mejor generación 

**Resumen**:extraer información clave para la generación de respuestas del documento reempaquetado y eliminar redundancias 

La implementación de RAG también requiere decisiones sobre las formas de dividir correctamente los documentos en fragmentos, los tipos de embeddings que se utilizarán para representar semánticamente estos fragmentos, la elección de
bases de datos vectoriales para almacenar de manera eficiente representaciones de features y métodos para ajustar eficazmente los LLM


El RAG tradicional funciona según un principio sencillo:

**Recuperación de información**: recupera información relevante de un documento o conjunto de documentos en función de la consulta del usuario.

**Prompt Augmentation**: la información recuperada se incorpora a la indicación para un modelo de lenguaje amplio (LLM).

**Generación de respuesta**: el LLM utiliza la indicación enriquecida para generar una respuesta, normalmente una respuesta a la pregunta del usuario


# Puntos necesarios para generar el RAG
A su vez el funcionamiento adecuado de un RAG depende de la correcta implementación  de sus 4 operaciones principales: 
### Indexing
    Por lo general, los datos a los que se hace referencia se convierten en embeddings de LLM, representaciones numéricas en forma de vectores. Estos embeddings se almacenan luego en una base de datos vectorial para permitir la recuperación de documentos.
### Retrieval
    Dada una consulta de usuario, primero se llama a un recuperador de documentos para seleccionar los documentos más relevantes que se utilizarán para augmentar la consulta. Esta comparación se puede realizar utilizando una variedad de métodos, que dependen en parte del tipo de indexación utilizada.
### Augmentation
    El modelo alimenta esta información recuperada relevante al LLM a través de prompt engineering de la consulta original del usuario. También se pueden incorporar módulos de aumento específicos con capacidades como expandir consultas a múltiples dominios y usar la memoria y la automejora para aprender de recuperaciones anteriores.

### Generation
    Por último, el LLM puede generar resultados basados ​​tanto en la consulta como en los documentos recuperados.Algunos modelos incorporan pasos adicionales para mejorar los resultados, como la reclasificación de la información recuperada, la selección del contexto y el fine-tuning.

Este último depende del modelo y no esta en manos del desarrollador mejorar el rendimiento de esta componente directamente, solo escoger el modelo que mejor funcione para el problema. Pero con las modificaciones correctas en las otras 3 fases es posible disminuir la dependencia del modelo en la parte de Generación

### A pesar de su eficacia, el RAG tradicional tiene varias limitaciones:

**Dependencia de la recuperación inicial**: la precisión de la respuesta del LLM depende en gran medida del paso de recuperación inicial. Si la información recuperada no coincide exactamente con la intención del usuario, la respuesta puede ser inexacta o irrelevante.

**Ciclo único de solicitud-respuesta**: el RAG tradicional generalmente se limita a un solo ciclo de solicitud-respuesta, lo que lo hace inadecuado para consultas complejas que requieren varios pasos o información de fuentes externas.

**Limitaciones de la ventana de contexto**: si bien algunos LLM pueden manejar contextos de gran tamaño, enviar un documento masivo al modelo puede ser ineficiente y costoso. Además, los límites de tokens de respuesta pueden restringir la profundidad de las respuestas generadas.

## Técnicas para mejorar el rendimiento de las componentes
### En la fase de Indexing influyen:
    La cantidad de contexto que retiene cada chunk
### Mejoras al Indexing
#### Parent Document Retriever
    Esta técnica consiste en cortar chunks grandes (chunks padre) en chunks aún más pequeños (chunks hijo). Al tener chunks pequeños, la información que contienen está más concentrada y por tanto, su valor informativo no se diluye entre párrafos de texto. Una vez hecho esto, realiza la búsqueda de los documentos top K más relevantes con los chunks hijo, y devuelve los trozos padres a los que pertenece el documento hijo top K

#### Contextual Embedding
    Anthropic introdujo este concepto para resolver el problema de la falta de contexto al agregar contexto relevante a cada fragmento antes de incrustarlo.


##### Prompt base usado de Anthropic para generar los embeddings contextuales
```python
<document> 
{{WHOLE_DOCUMENT}} 
</document> 
Here is the chunk we want to situate within the whole document 
<chunk> 
{{CHUNK_CONTENT}} 
</chunk> 
Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else. 
```
#### Notas
    Es posible una mezcla de Parent Document Retriever y Contextual Embeddings. Donde cada chunk hijo use el chunk padre como contexto para hacer la información contextual?
### En la fase de Retrieval influyen:
1. Que tan bien optimizado está el index y cuanta información se recupera[1](Los chunks. Se resuelve en fase de Indexing)

2. Que tan bien se optimiza la query 

#### Mejoras al Retrieval
###### Self Query Retriever
    Es aquel que, como sugiere su nombre, tiene la capacidad de realizar consultas a sí mismo. En concreto, dada cualquier consulta en lenguaje natural, el recuperador reconstruye la a una consulta estructurada y, a continuación, aplica esa consulta estructurada a su almacén de vectores subyacente. Esto permite al recuperador no solo utilizar la consulta de entrada del usuario para la comparación de similitud semántica con el contenido de los documentos almacenados, sino también extraer filtros de la consulta del usuario sobre los metadatos de los documentos almacenados y ejecutar esos filtros. Así solo se realizará la recuparación semántica en aquellos documentos almacenados que no sean filtrados por los metadatos

###### Contextual Compression Retriever (Reranking)
    Esta técnica consta de dos pasos muy diferentes:
    
    Paso 1: Obtener una buena cantidad de documentos relevantes en función del input/question. Normalmente se fiajn los K más relevantes.

    Paso 2: Recalcular cuáles de estos documentos son realmente relevantes. descartando los otros documentos que no sean realmente útiles (Compresión).

    Para el primer paso se utiliza lo que se conoce como Bi-Encoder, que no es más que lo que suele utilizar para hacer un RAG básico. Vectorizar los documentos. Vectorizar la consulta y calcular la similitud con cualquier métrica que elijamos.

    El segundo paso es algo diferente. Este recálculo/reranking lo ejecuta el modelo de reranking o cross-encoder.

###### Contextual Retrieval 
    Este método utiliza dos subtécnicas: embeddings contextuales y BM25 contextual. Este método puede reducir la cantidad de recuperaciones fallidas en un 49 % y, cuando se combina con la reclasificación, en un 67 %. Esto representa mejoras significativas en la precisión de la recuperación, lo que se traduce directamente en un mejor rendimiento en las tareas posteriores.

    El principal problema de este método yace en como combinar apropiadamente los resultados recuperados con las diferentes puntuaciones de ambos algoritmos. Esto generalmente se resuelve con la ayuda del algoritmo  Reciprocal Rank Fusion, reordenando los resultados recuperados para obtener el resultado final.

    La reclasificación es una técnica de filtrado que se utiliza con frecuencia para garantizar que solo los fragmentos más relevantes se pasen al modelo. La reclasificación proporciona mejores respuestas y reduce los costos y la latencia porque el modelo procesa menos información. Los pasos clave son:
    
    1. Realizar una recuperación inicial para obtener los fragmentos potencialmente más relevantes (usamos los 150 principales);
    
    2. Pasar los fragmentos N principales, junto con la consulta del usuario, a través del modelo de reclasificación;
    
    3. Utilizando un modelo de reclasificación, asigne a cada fragmento una puntuación en función de su relevancia e importancia para la solicitud, luego seleccione los fragmentos K principales (usamos los 20 principales);
    
    4. Pasar los fragmentos K principales al modelo como contexto para generar el resultado final

##### Notas
>* El uso de embeddings + BM25 es mejor que los embeddings por sí solos
>* Encontrar el número adecuados de chunks que pasarle al modelo(parece que los 20 fragmentos principales al modelo es más efectivo que solo los 10 o 5 principales)
>* Agregar contexto a los fragmentos mejora mucho la precisión de la recuperación;
>* Reclasificar es mejor que no hacerlo;

#### En la fase de  Augmentation influyen:

#### Mejoras al Augmentation
###### Reasoning Agent
    Agentic RAG introduce un elemento fundamental: el “agente”. Este agente actúa como un intermediario inteligente entre el usuario y el LLM, mejorando el proceso a través del razonamiento y el enrutamiento específico de tareas.

### Cómo funciona Agentic RAG

#### Reconocimiento de intenciones: 
    El agente primero analiza la pregunta del usuario para comprender su intención subyacente. Tomemos un ejemplo de preguntas y respuestas de Documentos: ¿el usuario busca un resumen? ¿Una comparación? ¿Detalles específicos?

#### Enrutamiento de tareas: 
    Según la intención, el agente enruta la pregunta del usuario a un subagente especializado. Este podría ser un “agente de resumen”, un “agente de comparación” o un agente capaz de obtener datos de fuentes externas a través de API (llamadas de funciones, etc.) o el mismo agente lo que usando distintos prompts como herramientas.

#### Procesamiento de varios pasos: 
    Agentic RAG permite el procesamiento de varios pasos. El agente puede realizar tareas adicionales antes de elaborar una respuesta, lo que genera resultados más precisos y completos.


### Componentes de un agente
#### Analizador de consultas

    El analizador de consultas desglosa la consulta de entrada para comprender su intención y contexto. Emplea técnicas de procesamiento del lenguaje natural (PLN) para extraer características y determinar el tipo de consulta.

#### Gestor de recuperación

    El gestor de recuperación es responsable de seleccionar y optimizar las estrategias de recuperación. Utiliza la información del analizador de consultas para decidir si se debe utilizar una recuperación dispersa, una recuperación densa o un enfoque híbrido. También gestiona la clasificación y la relevancia de los documentos recuperados.

#### Controlador de generación

    El controlador de generación ajusta los parámetros del modelo de generación en función del contexto proporcionado por el gestor de recuperación. Se asegura de que la respuesta generada sea coherente, contextualmente apropiada y relevante para la consulta de entrada.

#### Bucle de retroalimentación

    El bucle de retroalimentación supervisa el rendimiento de los procesos de recuperación y generación. Recopila los comentarios de los usuarios y las métricas de rendimiento del sistema para informar a los algoritmos de aprendizaje adaptativo del agente.

#### Módulo de aprendizaje adaptativo

    El módulo de aprendizaje adaptativo utiliza el aprendizaje por refuerzo para mejorar continuamente las estrategias del agente. Actualiza los procesos de toma de decisiones del agente en función de los datos de retroalimentación y rendimiento.