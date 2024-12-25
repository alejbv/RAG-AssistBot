message_history = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "Hello, who are you?"
    },
    {
        "role": "assistant",
        "content": "I am an AI created by OpenAI. How can I assist you today?"
    },
    {
        "role": "user",
        "content": "Can you help me with some programming questions?"
    },
    {
        "role": "assistant",
        "content": "Of course! What do you need help with?"
    }
]


def history(memory: int):
    if memory == 0:
        return []

    if memory == "all":
        messages = message_history
    else:
        messages = message_history[-memory:]

    return messages.copy()

def submit(
    query: str,
    memory: int = "all",
    role: str = "user",
    store: bool = True,
):
    messages = history(memory)
    if memory != "all":
        messages.insert(0, dict(role="system", content="You are a helpful assistant."))

    if store:
        messages.append(dict(role=role, content=query))

    print(messages)

submit("Hello, who are you?", memory=2)
print("history")
print(message_history)