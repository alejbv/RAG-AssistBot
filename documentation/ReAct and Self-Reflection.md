Un agente que tenga 3 habilidades fundamentales
1- Generar Respuesta de Leyes segun un contexto
2- Determinar donde falta informacion y generar queries para suplir dichas necesidades

3- Criticar la respuesta actual y determinar fallas e incosistencias, asi como arreglar errores

# Uso de Habilidades y Herramientas

  

# ReAct

Reasoning does not affect the external environment, thus leading to no observation feedback. Instead, a thought $a_t$ aims to compose useful information by reasoning over the current context $c_t$, and update the context $c_{t+1} = (c_t, a_t)$ to support future reasoning or acting. There could be various types of useful thoughts

- decomposing task goals and create action plans

- injecting commonsense knowledge relevant to task solving

- extracting important parts from observations

- track progress and transit action plans

- handle exceptions and adjust action plans

  

# Self-Reflection