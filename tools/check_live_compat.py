"""Check the pinned provider's patched result serializer without cloud credentials."""

import ast
import datetime
import sys
from pathlib import Path
from typing import Any

from google.genai import types
from homeassistant.helpers import llm


def main():
    source = Path(sys.argv[1]).read_text(encoding="utf-8")
    tree = ast.parse(source)
    helper = next(
        item
        for item in tree.body
        if isinstance(item, ast.FunctionDef) and item.name == "_validate_tool_results"
    )
    # Execute only the pure conversion helper, not the provider's integration/module.
    namespace = {"llm": llm, "datetime": datetime, "Any": Any}
    exec(
        compile(ast.Module(body=[helper], type_ignores=[]), "provider_serializer", "exec"),
        namespace,
    )
    convert = namespace["_validate_tool_results"]
    success = convert(llm.ToolResult(data={"expression": "happy"}))
    failure = convert(llm.ToolResult(data={"reason": "expired"}, error=True))
    assert success == {"expression": "happy"}
    assert failure == {"error": {"reason": "expired"}}
    assert convert({"nested": [llm.ToolResult(data={"ok": True})]}) == {"nested": [{"ok": True}]}
    for result in (success, failure):
        response = types.FunctionResponse(name="chan_set_expression", response=result)
        assert response.model_dump(mode="json")["response"] == result
    print("Gemini ToolResult serialization: success, error and nested values passed")


if __name__ == "__main__":
    main()
