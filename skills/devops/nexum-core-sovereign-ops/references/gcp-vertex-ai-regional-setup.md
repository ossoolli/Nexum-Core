# GCP Vertex AI Regional Setup for Nexum-Core

Detailed reference for configuring Google Vertex AI Generative AI (Gemini) SDK inside Nexum-Core and Hermes Agent, utilizing regional endpoints and service account keys.

## Credentials and Project Mapping
- **Service Account Key File:** `/home/madarmutaz/Nexum-Core/storage/gcp_key.json`
- **GCP Project ID:** `mytest-496209` (must match `project_id` in the JSON key file)
- **Service Account Email:** `vertex-express@mytest-496209.iam.gserviceaccount.com`

## Environment Configuration
Both Nexum-Core (`/home/madarmutaz/Nexum-Core/.env`) and Hermes Agent (`~/.hermes/.env`) must be configured with the following environment variables to ensure successful authentication and routing:

```env
GOOGLE_APPLICATION_CREDENTIALS=/home/madarmutaz/Nexum-Core/storage/gcp_key.json
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=mytest-496209
GOOGLE_CLOUD_LOCATION=us-central1
GEMINI_MODEL=gemini-2.5-flash
GEMINI_IMAGE_MODEL=gemini-2.5-flash
```

### Critical Gotchas and Pitfalls
1. **No Global Endpoints for Vertex AI Gemini:** Unlike the standard Google AI Studio Gemini API, Vertex AI predictions are strictly regional. If `GOOGLE_CLOUD_LOCATION` is left unset, or set to `global` (the default in some configs), Vertex AI API calls will fail with `404 NOT_FOUND` or `401 UNAUTHENTICATED`. Setting the region to `us-central1` resolves this immediately.
2. **Standard Gemini Models:** Standard API model identifiers like `gemini-1.5-flash` or `gemini-1.5-pro` may return `404 NOT_FOUND` under Vertex AI unless the exact mapped regional endpoint or versioned naming (e.g., `gemini-2.5-flash`) is used.
3. **Double GOOGLE_APPLICATION_CREDENTIALS Duplication:** Ensure there are no duplicate entries of `GOOGLE_APPLICATION_CREDENTIALS` in `.env` as they can confuse some parsers. Keep a single clean absolute path.
