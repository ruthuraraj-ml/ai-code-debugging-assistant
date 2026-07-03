from crewai_tools import CodeInterpreterTool

tool = CodeInterpreterTool()

print(tool)
print()

print(tool.args_schema)

print(tool.args_schema.model_json_schema())