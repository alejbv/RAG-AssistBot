### Arquitectura de una Aplicación con RAG
Descripción de la arquitectura básica que utilizan las aplicaciones basadas en RAG
1. La capa de orquestación recibe la entrada del usuario en cualquier metadato asociado (como el historial de conversaciones), interactúa con todas las herramientas relacionadas, envía el mensaje al LLM y devuelve el resultado. Las capas de orquestación suelen estar compuestas por herramientas como LangChain, Semantic Kernel y otras con un código nativo (a menudo Python) que une todo.

2. Las herramientas de recuperación son un grupo de utilidades que devuelven el contexto que informa y fundamenta las respuestas a las solicitudes del usuario. Este grupo abarca tanto las bases de conocimiento como los sistemas de recuperación basados ​​en API.

3. LLM es el modelo de lenguaje grande al que envías indicaciones. Pueden estar alojados por un tercero como OpenAI o ejecutarse internamente en tu propia infraestructura. Para los fines de este artículo, no importa el modelo exacto que uses.
## Puntos necesarios para generar el RAG
El funcionamiento adecuado de un RAG depende de la correcta implementación  de sus dos componentes principales: el Retriever  y el Generador. 
En el Retriever influyen mucho:
>* La fuente de información de la que se recupera
>* Que tan bien optimizado está el index
>* Que tan bien se optimiza la query 
>* El embedding que se utilizá

###### Paso 1: Generar embeddings
> Vector embedding son representaciones numéricas de datos que capturan relaciones semánticas y similitudes, lo que permite realizar operaciones matemáticas y comparaciones en los datos para diversas tareas como análisis de texto y sistemas de recomendación. O sea, son una forma de representar datos como puntos en un espacio n-dimensional de modo que los puntos de datos similares se agrupen.

Herramientas para generar embeddings:
>* [sentence_transformers](https://sbert.net/docs/sentence_transformer/pretrained_models.html)
>* [together](https://pypi.org/project/together/)
>* [hugging_face](https://huggingface.co/blog/getting-started-with-embeddings)
###### Paso 2: Base de datos vectorial
Para consultar los datos, no solo se necesitan los datos, sino que también se necesitan en un formato que sea accesible para la aplicación. Para las aplicaciones basadas en LLM, esto generalmente implica un almacén de vectores, una base de datos que puede realizar consultas en función de la similitud textual en lugar de coincidencias exactas. Como:
>* FAISS
>* Astra DB
>* Chroma DB
>* Pinecone

Algo a tener en cuenta es el cargar el contenido de los documentos en la memoria. Herramientas como Unstructured, LlamaIndex y los cargadores de documentos de LangChain permiten cargar todo tipo de documentos en las aplicaciones, en particular contenido no estructurado.
###### Paso 3: Recuperacion de información(Semantic Search)
En pocas palabras, la búsqueda semántica funciona comparando embedding de oraciones: se busca un resultado cuyo embedding sea cercano al embedding de la consulta. Esta búsqueda tiende a ser más lenta que la léxica, una buena idea sería usar léxical search para recuperar los documentos iniciales y luego usar un modelo semántico para realizar rerank a los documentos recuperados[^1].
 
[^1]:Considerar investigar Contextual RAG para mejorar la fase de Retreival .

El problema es que las soluciones RAG tradicionales eliminan el contexto al codificar la información, lo que a menudo provoca que el sistema no pueda recuperar la información relevante de la base de conocimientos.

Pero existe un método que mejora drásticamente el paso de recuperación en RAG. El método se llama ["Recuperación contextual"](https://www.anthropic.com/news/contextual-retrieval) y utiliza dos subtécnicas: embeddings contextuales y BM25 contextual. Este método puede reducir la cantidad de recuperaciones fallidas en un 49 % y, cuando se combina con la reclasificación, en un 67 %. Esto representa mejoras significativas en la precisión de la recuperación, lo que se traduce directamente en un mejor rendimiento en las tareas posteriores.

El principal problema de este método yace en como combinar apropiadamente los resultados recuperados con las diferentes puntuaciones de ambos algoritmos. Esto generalmente se resuelve con la ayuda del algoritmo **Reciprocal Rank Fusion**, reordenando los resultados recuperados para obtener el resultado final.

Otra forma de mejorar la recuperación está en optimizar la forma en que se recuperan los chunks. Un ejemplo de estas herramientas son:
>* **Índices jerárquicos**: La idea es crear dos índices, uno compuesto de resúmenes y el otro compuesto de fragmentos de documentos, y buscar en dos pasos, primero filtrando los documentos relevantes por resúmenes y luego buscando solo dentro de este grupo relevante.
>* **Preguntas Hipoteticas y HyDE**: Otro enfoque es pedirle a un LLM que genere una pregunta para cada chunk e incorpore estas preguntas en vectores, en tiempo de ejecución, realizar una búsqueda de consulta contra este índice de vectores de preguntas (reemplazando los vectores de chunks con vectores de preguntas en nuestro índice) y luego, después de la recuperación, dirigirse a los chunks de texto originales y enviarlos como contexto para que el LLM obtenga una respuesta. Este enfoque mejora la calidad de la búsqueda debido a una mayor similitud semántica entre la consulta y la pregunta hipotética en comparación con lo que tendríamos para un fragmento real. También existe el enfoque de lógica inversa llamado HyDE: se le pide a un LLM que genere una respuesta hipotética dada la consulta y luego se usa su vector junto con el vector de consulta para mejorar la calidad de la búsqueda.
>* **Enriquecimiento del Contexto**: El concepto aquí es recuperar fragmentos más pequeños para lograr una mejor calidad de búsqueda, pero agregar el contexto circundante para que LLM pueda razonar sobre él.
>> 1. **Recuperación de la ventana de oraciones**: En este esquema, cada oración de un documento se integra por separado, lo que proporciona una gran precisión en la búsqueda de la distancia del coseno entre la consulta y el contexto. Para poder razonar mejor sobre el contexto encontrado después de obtener la oración individual más relevante, ampliamos la ventana de contexto con k oraciones antes y después de la oración recuperada y luego enviamos este contexto ampliado a LLM.
>> 2. **Recuperador de documentos primarios**: La idea aquí es bastante similar a la del recuperador de ventana de oraciones: buscar fragmentos de información más granulares y luego ampliar la ventana de contexto antes de enviar dicho contexto a un LLM para que razone. Los documentos se dividen en fragmentos secundarios más pequeños que hacen referencia a fragmentos primarios más grandes. Primero se recuperan los fragmentos más pequeños durante la recuperación y, luego, si más de n fragmentos en los k fragmentos recuperados principales están vinculados al mismo nodo primario (fragmento más grande), reemplazamos el contexto enviado al LLM por este nodo primario; funciona como la fusión automática de algunos fragmentos recuperados en un fragmento primario más grande, de ahí el nombre del método.
### Notas
>* El uso de embeddings + BM25 es mejor que los embeddings por sí solos
>* Encontrar el número adecuados de chunks que pasarle al modelo(parece que los 20 fragmentos principales al modelo es más efectivo que solo los 10 o 5 principales)
>* Agregar contexto a los fragmentos mejora mucho la precisión de la recuperación;
>* Reclasificar es mejor que no hacerlo;


###### Paso 4: Modelo de chat
El siguiente gran paso en la creación de un buen sistema RAG que pueda funcionar más de una vez para una sola consulta es la lógica del chat, que tiene en cuenta el contexto del diálogo.
Esto es necesario para admitir preguntas de seguimiento, anáforas o comandos de usuario arbitrarios relacionados con el contexto del diálogo anterior. Se soluciona mediante la técnica de compresión de consultas, que tiene en cuenta el contexto del chat junto con la consulta del usuario.
###### Paso 5: Herramientas(Prompts) para manejar el flujo de las operaciones
Existen varias técnicas para mejora las respuestas que dan los LLM. Entre estas están:
>* Chain of Thought
>* Self-Consistency (Is like a Few-ShotCoT)
>* Prompt Chaining (Una tarea se divide en subtareas con la idea de crear una cadena de operaciones de prompt.)
>* Tree of Thoughts (Tareas complejas que requieren exploración o una visión estratégica anticipada)
```python
"""
System:  {system_instruction} // Basicamente la  instrucción que le das al modelo sobre como responder  a tu pregunta. Aqui le debes aclarar que use el  historial y el contexto
History: {history} //historial de conversaciones con el usuario
Context: {context} // contexto que el modelo debe usar como base de conocimiento
User: {request} // La petición realizada por el usuario
"""
```
###### Paso 6: Vincular los 3 puntos anteriores para generar la respuesta
>* Query Routing
>* Agents
## Ideas para mejorar el desempeño
>* Ajustar la estrategia de división. Experimentar con diferentes tamaños de chunks de texto para asegurarse de que su inferencia habilitada para RAG mantenga el contexto adecuado. Cada conjunto de datos es diferente. Se debe crear diferentes almacenes de vectores divididos y ver cuál funciona mejor con la arquitectura.
> 
>* Ajustar el system prompt. Si el LLM no presta suficiente atención al contexto, se debe actualizar el mensaje del sistema con expectativas sobre cómo procesar y usar la información proporcionada.
>
>* Filtrar los resultados del almacén de vectores. Si hay tipos de contenido en particular que se desea o no que se muestren, filtrar los resultados del almacén de vectores según los valores de los elementos de metadatos.
>
>* Probar distintos modelos de embeddings (y si es posible desarrollar uno adecuado). Los distintos modelos de embeddings tienen distintas formas de codificar y comparar vectores de los datos. Se debe experimentar para ver cuál funciona mejor para la aplicación. Consultar los modelos de embeddings de código abierto con mejor rendimiento en la tabla de clasificación de MTEB. También se puede perfeccionar modelos de embeddings para que el LLM conozca mejor la terminología específica del dominio y, por lo tanto, brinde mejores resultados de consulta. Y sí, se puede, utilizar un conjunto de datos de base de conocimiento limpio y procesado para perfeccionar el modelo.
>
>* Usar alguna forma caching para mejorar el desempeño y no tener que estar constantemente realizando llamadas al LLM para preguntas frecuentes
### Ventajas del RAG
Como se explica en la arquitectura RAG, se puede forzar a al modelo LLM a restringirse a la información que se encuentra en los documentos relevantes. Esto garantiza que la alucinación (es decir, las respuestas sin sentido) tengan poco chance de ocurrir

Estos permiten un diseño conversacional para permitir un diálogo complejo.Permitiendo que el usuario puedea ampliar la respuesta proporcionada por su solución.

Prompt engineering como una forma de dirigir la generación hacia el éxito lo que permite obtener la respuesta del LLM de manera precisa, se le debe decir al modelo exactamente qué tipo de resultado espera. En general, esto no es nada complicado.
### Defecto de RAG
Cabe señalar que el enfoque RAG, impulsado por un LLM general, solo funciona bien siempre que la base de conocimientos específica no contenga una jerga súper específica que el LLM no pueda comprender a partir de su formación general.

El Fine-tuning es una mejor opción cuando se necesita que las respuestas de la solución sigan "el tono y la jerga" presentes en la base de conocimientos.

Podría ser un enfoque válido poder manejar jerga específica y luego incorporar el LLM con Fine-tuning en la arquitectura RAG para cosechar los beneficios combinados.

## Bibliografía 
1. [Retrieval Augmented Generation (RAG) for LLMs](https://www.promptingguide.ai/research/rag)
2. [Prompt Engineering](https://medium.com/the-generator/the-perfect-prompt-prompt-engineering-cheat-sheet-d0b9c62a2bba)
3. [Advanced RAG](https://pub.towardsai.net/advanced-rag-techniques-an-illustrated-overview-04d193d8fec6)
