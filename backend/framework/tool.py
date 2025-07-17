import inspect
from typing import Callable

class Tool:
    def __init__(self, name: str, description: str ,func: Callable[[str], str]):
        self.name = name
        self.description = description.strip()
        self.func = func
        self.signature = inspect.signature(func)

    @classmethod
    def create_tool(cls, target:Callable) -> "Tool":
        """Class function for generate a tool from the target function only

        Args:
            target (Callable): The function on which you generate the tool

        Returns:
            Tool: The tool created
        """
        
        name = target.__name__
        description = inspect.getdoc(target) or ""
        return cls(name, description, target)
    
    def __repr__(self) -> str:
        
        # The parameters from the function 
        parameters = {param.name:{"type": param.annotation} for param in self.signature.parameters.values()}
        
        # The parameters required for the function
        required = [
                param.name
                for param in self.signature.parameters.values()
                if param.default == inspect._empty
            ]
        
        function_schema = {
        "type": "function",
        "function": {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }
        return str(function_schema)
        
    async def use(self, query: str) -> str:
        try:
            if inspect.iscoroutinefunction(self.func):
                result = await self.func(query)
            else:
                result = self.func(query)
            return result
        except Exception as e:
            return str(f"Error executing tool {self.name}: {e}")
