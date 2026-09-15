class FrameException(Exception):
    """框架级别的异常处理"""
    pass

class AgentException(FrameException):
    """Agent 异常处理"""
    pass

class LLMException(FrameException):
    """大模型异常"""
    pass

class ToolException(FrameException):
    """工具异常"""
    pass