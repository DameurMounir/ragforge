# Revision-bound retrieval and citations

Upload and process the document using the documents API, then index its chunks. On TXT and PDF uploads the owner stores a SHA-256 digest of the original bytes. Processing reads a private snapshot, checks the upload digest if present, and attaches the following metadata to each passage.

| Field | Meaning |
| --- | --- |
| `source_revision` | SHA-256 of the raw source file, in lowercase hexadecimal |
| `page_number` | One-based PDF page, or 1 for a TXT file |
| `char_start`, `char_end` | Zero-based Unicode offsets in the extracted page. The end is exclusive |
| `passage_sha256` | SHA-256 of the UTF-8 passage returned by the API |

Existing uploads without a digest can be processed using the bytes available at reprocessing time. Reprocessing and reindexing are necessary for older passages to acquire this metadata. A passage location refers to the extracted Unicode text, which can differ from the raw byte offsets or the visual reading order in a PDF.

## Compare a selected pair

For each source selected by the application, verify its current authorization and resolve the expected project, asset and revision. Perform a separate asset-scoped search for each side, with text and metadata included. Check the returned project mapping, asset, revision and passage digest before using the text. Repeat the authorization and source check when opening a citation or recording a review. Treat a missing side as incomplete.

The default dense route preserves its current score and wire format. `SEARCH_REQUIRE_MATCHING_EMBEDDING_SPACE=true` restricts the vector search to the embedding provider and model that produced the query. Reindex historical vectors that lack these fields before enabling this setting. A provider alias that changes the underlying model needs a new index generation and a qualified cutover.

## Extractive answer policy

`POST /api/v1/answers/{project_id}` accepts `citation_policy: "verbatim"`. Include the authorized asset ID and a question in the normal request. In this policy the service compares each cited sentence with the actual passages in the model's context. An unsupported sentence triggers `rag_answer_review_required`. Callers should surface the review signal even when some supported sentences remain.

This policy verifies source attribution and copied wording. A downstream application still owns the interpretation of values, exceptions, document versions, currency and permissions. The default policy checks citation numbers. A wholly unknown citation now produces abstention instead of an unsupported statement with its citation stripped.

## Retrying partial vector writes

When a vector provider acknowledges only a count, a short count cannot identify individual successful records. The service marks only a fully acknowledged batch as indexed. Retry unconfirmed chunks with the same vector record IDs. Ordinary incremental retries are covered. The existing explicit reset operation deletes scoped vectors before rebuilding and must be planned separately.

## Request ranked passages from one document

Send a service-authenticated `POST /api/v1/search/{project_id}` with the expected asset and the full lowercase SHA-256 resolved by the caller's authorized source catalog. The example uses placeholder identifiers. Choose `bm25` for lexical retrieval or `rrf` to fuse lexical and dense rankings.

```json
{
  "query": "REF-RH-07 indemnité de déplacement",
  "asset_id": "0123456789abcdef01234567",
  "source_revision": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "ranking_method": "rrf",
  "max_corpus_chunks": 64,
  "max_corpus_characters": 120000,
  "limit": 5,
  "include_text": true,
  "include_metadata": true
}
```

Both budgets apply to the entire pinned document. The service accepts 1–256 chunks, 1–1,000,000 extracted Unicode characters and queries up to 4,096 characters for these modes. The result limit also obeys the configured server maximum. Requests over either corpus budget receive HTTP 413. An incomplete index, missing current asset digest, mismatched revision or changed asset receives HTTP 409. For a historical upload lacking an owner-bound digest, upload the verified source as a new asset, process and index it, then select the new identity. Historical chunk metadata alone cannot activate the ranked modes.

BM25 searches all eligible passages. Its wire score is `BM25 / (1 + BM25)`. RRF uses the sum of `1 / (60 + rank)` over each input list in which the passage occurred. It constrains the dense lookup by project, asset, revision, provider and model. With metadata enabled, results include `raw_rank_score`, `lexical_rank` and `dense_rank`. A missing rank is null. The response signal names the method even when metadata is hidden. These scores express relative ranking within the requested corpus. A `min_score` supplied with either mode receives HTTP 422. Omit all ranked options for the existing dense search.
