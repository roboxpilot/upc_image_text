from fastapi import HTTPException

class APICallError(HTTPException):
    def __init__(self, model: str, detail: str):
        super().__init__(status_code=500, detail=f"Error in {model.capitalize()} API call: {detail}")

class JSONParseError(HTTPException):
    def __init__(self):
        super().__init__(status_code=500, detail="Failed to parse LLM response as JSON")

class InvalidModelError(ValueError):
    def __init__(self, model: str):
        super().__init__(f"Invalid model selected: {model}")