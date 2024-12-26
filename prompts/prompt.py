EXTRACT_INFORMATION_SYSTEM_PROMPT = """You are a helpful assistant. Your task is to help answer a question given in a document. 
The first step is to extract quotes relevant to the question from the document, delimited by ####. 
Please output the list of quotes using <quotes></quotes>. Respond with "No relevant quotes found!" if no relevant quotes were found.
####
{{document}}
####
"""
#################################################################################################
RESPONSE_INFORMATION_SYSTEM_PROMPT = """Given a set of relevant quotes (delimited by <quotes></quotes>) extracted from a document
and the original document (delimited by ####), please compose an answer to the question. 
Ensure that the answer is accurate, has a friendly tone, and sounds helpful.
####
{{document}}
####
"""
######################################################################################
BASIC_SYSTEM_PROMPT = """Eres un asistente servicial y amigable.
Responde la pregunta usando el contexto más abajo. Si la
pregunta no puede ser respondida con la información provista
responde con "Lo siento, pero no puedo responder tu pregunta."
Mantén la respuesta concisa
Context: {Context}.

Question: {Question}

Answer: """

DEFAULT_SYSTEM_PROMPT = """Eres un asistente para tareas de preguntas y respuestas.
Utiliza los siguientes fragmentos de contexto recuperados para responder
la pregunta. Si no sabes la respuesta, di que
no sabes. Usa tres oraciones como máximo y mantén la
respuesta concisa.
\n\n
{context}
"""
DEFAULT_USER_PROMPT = "{query}"

###############################################################################
GENERATE_CHUNKS_PROMPT="""
<document> 
{{WHOLE_DOCUMENT}} 
</document> 
Here is the chunk we want to situate within the whole document 
<chunk> 
{{CHUNK_CONTENT}} 
</chunk> 
Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. 
Answer only with the succinct context and nothing else. 
"""
###################################################################################
BASIC_PROMPT ="""
System:  {system_instruction} // Basicamente la  instrucción que le das al modelo sobre como responder  a tu pregunta. Aqui le debes aclarar que use el  historial y el contexto
History: {history} //historial de conversaciones con el usuario
Context: {context} // contexto que el modelo debe usar como base de conocimiento
User: {request} // La petición realizada por el usuario
"""
#####################################################################################
CoT_Prompt = """Analyze the following logical puzzle thoroughly. Follow these steps in your analysis:

List the Facts:

Summarize all the given information and statements clearly.
Identify all the characters or elements involved.
Identify Possible Roles or Conditions:

Determine all possible roles, behaviors, or states applicable to the characters or elements (e.g., truth-teller, liar, alternator).
Note the Constraints:

Outline any rules, constraints, or relationships specified in the puzzle.
Generate Possible Scenarios:

Systematically consider all possible combinations of roles or conditions for the characters or elements.
Ensure that all permutations are accounted for.
Test Each Scenario:

For each possible scenario:
Assume the roles or conditions you've assigned.
Analyze each statement based on these assumptions.
Check for consistency or contradictions within the scenario.
Eliminate Inconsistent Scenarios:

Discard any scenarios that lead to contradictions or violate the constraints.
Keep track of the reasoning for eliminating each scenario.
Conclude the Solution:

Identify the scenario(s) that remain consistent after testing.
Summarize the findings.
Provide a Clear Answer:

State definitively the role or condition of each character or element.
Explain why this is the only possible solution based on your analysis.
Scenario:

{scenario}

Analysis:"""
#################################################################################
CONTEXTUALIZE_Q_SYSTEM_PROMPT = """Dado un historial de chat y la última pregunta del usuario
que podría hacer referencia al contexto en el historial de chat,
formule una pregunta independiente que pueda entenderse
sin el historial de chat. NO responda la pregunta,
solo reformúlela si es necesario y, de lo contrario, devuélvala tal como está."""

