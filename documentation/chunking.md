# Why Chunking

Let’s start with the basics. The retrieved chunks will be fed directly into the prompt as context for your LLM to generate a response. This means that at the very minimum, the total length of all of the retrieved chunks combined cannot exceed the context window of the LLM. Though many LLMs today have generous context windows, you still may not want to fill up the context window to the brim, as these LLMs will struggle with the “needle in the haystack” problem. You may also want to utilize that large context window in additional ways, such as providing thorough instructions, a persona description, or some few-shot examples.

Additionally, if you intend to employ similarity search and embed your documents, you have to consider that embedding models also have a limited context window. These models cannot embed text that surpasses the maximum length of their context window. This limit varies depending on the specific model.

## Summary
- In first place the context windows of LLM have limited size 

- In second place to much unrelated context can affect the model capacities to response 

- The context window of the embedding have also limited size



En la fase de recuperación es importante de que los embeddings sean capaces de contener toda la información necesaria a la hora de hacer comparación 