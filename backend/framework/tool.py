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
        # type_map = {
        #     str: "string",
        #     int: "integer",
        #     float: "number",
        #     bool: "boolean",
        #     list: "array",
        #     dict: "object",
        #     type(None): "null",
        # }

        
        
        # # The parameters from the function 
        # signature = inspect.signature(self.func)
        # parameters = {}
        # for param in signature.parameters.values():
        #     try:
        #         param_type = type_map.get(param.annotation, "string")
        #     except KeyError as e:
        #         raise KeyError(
        #             f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
        #         )

        #     if param.default == inspect._empty:
        #         parameters[param.name] = param_type
    
        
        # return {name: type for name, type in parameters.items() if name != "return"}
        args = inspect.get_annotations(self.func)
        return {name: type for name, type in args.items() if name != "return"}
            
    async def use(self, **kwargs) -> str:
        return await self.func(**kwargs)

