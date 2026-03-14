# Anomaly Detection Agent

The anomaly detection agent is responsible for classifying likely integrity failures in a synthetic record or evidence bundle.

Core responsibilities:

- flag evidence tampering indicators
- identify suspicious timestamp orderings
- detect unauthorized generation paths
- surface unexpected transforms or reuse patterns

This role should report uncertainty when the available provenance is incomplete. It is a benchmarkable classifier, not a claim of production autonomy.
