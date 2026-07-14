# Provider Configuration

## Offline demo

The default needs no credential:

```dotenv
LLM_PROVIDER=demo
LLM_MODEL=demo-v1
```

It is a deterministic rule engine and is suitable for tests, screenshots, and app tours. It
is not a language model.

## OpenAI-compatible live adapter

Create a local `.env` that is ignored by Git:

```dotenv
LLM_PROVIDER=openai_compatible
LLM_MODEL=replace_with_a_current_compatible_model
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2
LLM_TEMPERATURE=0
```

Never paste the actual key into source code, screenshots, test output, issue reports, or
commits. `LLM_BASE_URL` is optional for a compatible endpoint. Compatibility is not
guaranteed: a service must support the SDK request fields and JSON-object response mode used
by the adapter.

Model catalogs and pricing change. For OpenAI, check the current official
[model catalog](https://developers.openai.com/api/docs/models) and
[comparison page](https://developers.openai.com/api/docs/models/compare) immediately before
testing.

## Safe verification sequence

1. Run the default tests; they make zero network calls.
2. Use one small synthetic English report and request English output.
3. Use one small synthetic Chinese report and request Chinese output.
4. Confirm success, prompt/model attribution, validity, token information from the provider,
   latency, and exact evidence.
5. Calculate the planned batch: evaluation is 180 outputs and 240 base semantic calls.
6. Add expected retries/repair, estimate input/output tokens using the two samples, look up
   current per-token prices, and present a range.
7. Obtain explicit approval before a full live run.

Authentication, rate-limit, timeout, connection, bad-request, missing-model, empty-response,
and malformed-response problems are translated into internal failures. Error strings are
truncated and key-like content is redacted.

