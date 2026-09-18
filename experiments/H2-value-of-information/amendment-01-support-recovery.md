# Amendment 01 — interleaved support recovery

Date: 2026-08-10  
Timing: after H2 exploratory seeds 500–599; before any H2 confirmatory seed was
opened.

## Trigger

The first pure VOI implementation retained zero wrong releases but failed the
registered exploratory utility targets: pooled coverage changed from `0.176`
for the frozen H1 adaptive policy to `0.174`, and certified goodput changed by
`-1.14%`. It improved the difficult compound-shift family but over-concentrated
attempts around the current worst certificate edge in easier families.

## Frozen correction

The 20 post-initial attempts now alternate deterministically:

- even-numbered refinement attempts use the frozen H1 gap/phase/uncertainty
  ranking as a support-recovery guard;
- odd-numbered refinement attempts use the registered VOI certificate-margin
  ranking.

The first refinement is a support-recovery step. Initial locations, total
budget, candidate fractions, VOI weights, certificate gates, hypotheses and
confirmatory seeds are unchanged. The method remains observed-data-only.

## Rationale and boundary

The guard supplies angular coverage while the VOI step targets the limiting
certificate edge. This amendment was selected on exploratory data and therefore
does not constitute confirmatory evidence. No further policy change is allowed
after opening seeds 2000–2099.

