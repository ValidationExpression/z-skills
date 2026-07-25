# Checkout incident review

## Timeline

[09:12]

On-call: Checkout latency increased after the regional cache configuration was deployed.

[09:18]

Database lead: Database CPU stayed below 45 percent and query latency remained normal.

[09:26]

On-call: Rolling back the cache configuration restored checkout latency within four minutes.

## Follow-up

Incident commander: The strongest current explanation is cache-key fragmentation. Packet loss was observed later, so the team has not established it as the initiating cause.
