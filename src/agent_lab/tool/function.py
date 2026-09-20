import inspect
from collections.abc import Callable
from typing import Any

from .base import Tool, ToolParameter
from .response import ToolResponse, ToolError


class FunctionTool(Tool):

    def __init__(self, func: Callable[..., Any]):
        self.func = func

        name = func.__name__

        description = inspect.getdoc(func) or ""

        parameters: list[ToolParameter] = []
        signature = inspect.signature(func)

        for parameter in signature.parameters.values():
            # 通过反射机制获取 属性 然后组装 工具参数
            required = parameter.default is inspect.Parameter.empty
            default = (
                None
                if required
                else parameter.default
            )

            tool_param = ToolParameter(
                name=parameter.name,
                annotation=parameter.annotation,
                required=required,
                description="",
                default=default
            )
            parameters.append(tool_param)

        super().__init__(
            name=name,
            description=description,
            parameters=parameters
        )

    def _run(self, arguments: dict[str, Any]) -> ToolResponse:
        try:
            result = self.func(**arguments)
            data = result if isinstance(result, dict) else {"result": result}
            return ToolResponse.success(
                text=str(result),
                data=data,
            )
        except Exception as exc:
            return ToolResponse.error(
                error_info=ToolError(
                    type = type(exc).__name__,
                    message = str(exc)
                )
            )
