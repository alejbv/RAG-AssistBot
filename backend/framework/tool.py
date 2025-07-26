import inspect
from typing import Callable
from pydantic import BaseModel
class Tool(BaseModel):
    name: str
    description: str
    func: Callable
    
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
        return cls(name=name, description=description, func=target)
    
    
    def parameters(self):
        """Function to get the parameters of the function"""
        args = inspect.get_annotations(self.func)
        return {name: type for name, type in args.items() if name != "return"}
            
    async def run(self, **kwargs) -> str:
        return await self.func(**kwargs)

