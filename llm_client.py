from huggingface_hub import InferenceClient

SYSTEM_PROMPT = """
Eres un bot de asistencia de la Universidad de La Habana. Responde con un lenguaje sencillo, cordial y siendo lo 
más descriptivo posible usando el lenguaje natural.
"""
USER_PROMPT = """
{input}
"""
from utils import load_data

class LLMClient:
    def __init__(self,data_api_key,data_model):
        self.client = InferenceClient(model=data_model,token=data_api_key)
    
    def chat(self,prompt_text, username):
        
        # Build the conversation history (SYSTEM_PROMPT, USER_PROMPT should be provided as usual)
        conversation = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(input=prompt_text)}
        ]
        
        # adding a completion
        completion = self.client.chat.completions.create(
            messages=conversation,
            max_tokens=128,
            temperature=0.3,
        )
        response = completion.choices[0].message.content
        return response
"""
    def ai_img_generation(self,prompt_text, username):
        # generating image
        response = openai.Image.create(
            prompt= prompt_text,
            n=1,
            size="1024x1024"
        )
        # get image url from response
        image_url = response['data'][0]['url']
        return image_url
"""

def main():
    data = load_data()
    api_key = data['API_KEY']
    model = data['MODEL']
    client = LLMClient(api_key,model)
    ###
    msg = "Who was the president of the United States in 2020"
    usr = "Alex"
    print(client.chat(msg,usr))
if __name__ == '__main__':
    main()