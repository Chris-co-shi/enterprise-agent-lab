from agent_lab.tool.function import FunctionTool


def add(a: int , b: int = 1):
    return a+ b



if __name__ == '__main__':
    tool = FunctionTool(add)
    print(tool.name)
    print(tool.parameters)
    print(tool.run({"a":1,"b":2}))