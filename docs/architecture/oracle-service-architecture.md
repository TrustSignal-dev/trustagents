# Oracle Service Architecture (Experimental)

The service is a compact FastAPI application with deterministic pipeline stages:

1. intake and canonical fingerprinting
2. claim extraction and normalization
3. source retrieval (mock, file, optional HTTP connector)
4. field comparison
5. risk flag generation
6. conservative policy evaluation
7. deterministic adjudication
8. bounded audit trace assembly

The API layer depends on the oracle service contract only. The oracle service depends on local deterministic components. No production TrustSignal integration code is included.
