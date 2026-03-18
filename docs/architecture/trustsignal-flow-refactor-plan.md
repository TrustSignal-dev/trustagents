# TrustSignal Operating Model Alignment (Minimal Increment)

## Scope of this increment

This increment introduces explicit pipeline stages, deterministic versioned scoring metadata, manual review routing, and a shadow case-memory subsystem. It keeps the repository simulation-oriented and avoids autonomous online learning.

## Current and added pipeline stages

1. fingerprinting/intake
2. extraction/normalization
3. retrieval/screening
4. fraud signal generation + policy checks
5. adjudication + review routing
6. receipt construction
7. anchoring

## Data model additions

- `decision` (`PROCEED`, `MANUAL_REVIEW`, `BLOCK`)
- `fraudRisk` object with score/band/confidence/top signals/scoring mode/review recommendation/similar cases
- `versions` object:
  - `riskModelVersion`
  - `policyVersion`
  - `signalSetVersion`
  - `reviewPolicyVersion`
- `signedReceipt`
- `anchorRecord`
- `manualReviewRequired`
- reviewed-case and reviewer-feedback payloads for shadow learning

## API additions

- `GET /api/v1/oracle/review-queue`
- `POST /api/v1/oracle/review-cases`
- `POST /api/v1/oracle/review-feedback`

## Review routing policy in this increment

Route to manual review when one or more conditions are met:

- fraud risk band is `MEDIUM` or `HIGH`
- ambiguity or near-match signals
- incomplete source/registry coverage
- low extraction confidence
- conflicting source fields

Hard blocks stay rule-based for:

- `revoked`
- `sanctions_match`
- `integrity_failure`
- `impossible_policy_contradiction`

## Learning-from-past approach

- Reviewed cases are persisted in a local in-memory shadow store.
- Similar-case retrieval is used for explanation/ranking support only.
- No live threshold auto-updates are performed.
- Any future scoring/policy updates require explicit version changes.

## Migration strategy from current deterministic oracle

1. Keep existing endpoint (`/api/v1/oracle/evaluate`) and existing fields.
2. Add new fields in response as backward-compatible extensions.
3. Introduce review queue + reviewed-case APIs for operator workflows.
4. In a later increment, externalize reviewed-case persistence to a file-backed or DB-backed audited store.
5. In a later increment, add explicit receipt verification and revocation lifecycle endpoints.

## Known missing pieces after this increment

- durable storage for review queue and case memory
- explicit registry adapter configuration and multi-source sanctions feeds
- separate receipt verification API and revocation lifecycle API
- signed key management and external anchor network integration
- offline retraining/reweighting workflow with formal approval gates
