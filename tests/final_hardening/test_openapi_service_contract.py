from src.ragforge.main import app


PROTECTED = {
    "/api/v1/documents/upload/{project_id}",
    "/api/v1/documents/process/{project_id}",
    "/api/v1/indexing/{project_id}",
    "/api/v1/search/{project_id}",
    "/api/v1/answers/{project_id}",
    "/api/v1/llm/generate",
}
REQUIRED_SUCCESS_SCHEMAS = {
    "/api/v1/health/",
    "/api/v1/documents/upload/{project_id}",
    "/api/v1/documents/process/{project_id}",
    "/api/v1/indexing/{project_id}",
    "/api/v1/search/{project_id}",
    "/api/v1/answers/{project_id}",
}


def _method(path: str) -> str:
    return "get" if path == "/api/v1/health/" else "post"


def test_openapi_declares_service_bearer_and_protected_operations() -> None:
    document = app.openapi()
    scheme = document["components"]["securitySchemes"]["RAGForgeServiceBearer"]
    assert scheme["type"] == "http"
    assert scheme["scheme"] == "bearer"
    for path in PROTECTED:
        operation = document["paths"][path]["post"]
        assert {"RAGForgeServiceBearer": []} in operation["security"]
    assert "security" not in document["paths"]["/api/v1/health/"]["get"]


def test_required_operations_have_concrete_success_schemas() -> None:
    document = app.openapi()
    for path in REQUIRED_SUCCESS_SCHEMAS:
        operation = document["paths"][path][_method(path)]
        response = next(
            value
            for code, value in operation["responses"].items()
            if str(code).startswith("2")
        )
        schema = response["content"]["application/json"]["schema"]
        assert schema
        assert "$ref" in schema or schema.get("properties")
