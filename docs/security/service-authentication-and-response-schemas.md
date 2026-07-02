
# RAGForge service authentication and response-schema hardening

## Boundary

RAGForge owns upload, processing, indexing, search, answers, and raw LLM generation.
Sherizon Control Plane owns user/tenant authorization, project mapping, usage, quota,
billing, and audit. RAGForge authenticates only the trusted calling service.

## Authentication

Business routes require the OpenAPI scheme `RAGForgeServiceBearer`. The bearer value
is loaded for each request from a regular, single-link, owner-validated file with no
group/world access. The implementation uses constant-time comparison and never logs,
returns, or embeds the secret. Production configuration fails closed when service
authentication is disabled or incomplete.

Health remains public for local liveness. Metrics remain governed by the deployment
boundary. Nginx explicitly forwards `Authorization` to the application.

## Response contracts

Health, upload, process, indexing, search, and answer declare concrete Pydantic success
models. Successful service payloads are validated before response emission; error
responses keep their existing status-specific JSON envelopes.

## Deployment gate

1. Generate the token file with `scripts/deployment/ragforge-create-service-token.sh`.
2. Mount it read-only through `RAGFORGE_SERVICE_AUTH_TOKEN_SOURCE`.
3. Validate Compose and run the complete test suite.
4. Deploy only to non-production first.
5. Prove missing and wrong credentials return 401 and the correct credential succeeds.
6. Capture the hardened OpenAPI and run the Sherizon 28F binding validator.
7. Execute the governed upload/process/index/search/answer smoke pipeline.
