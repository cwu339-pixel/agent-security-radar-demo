# Workflow Design

## Design Principle

This system should be understood as a `continuous sourcing workflow`, not as a chatbot.

The main product is not conversation. The main product is an investor-ready ranking of companies supported by evidence.

## End-to-End Workflow

### 1. Source Ingestion

Adapters collect representative signals from sources such as:

- X / Twitter
- LinkedIn
- GitHub
- news
- official websites
- research and databases

Each signal is normalized into a common schema so later stages do not need source-specific logic.

### 2. Relevance And Universe Classification

Before ranking anything, the system determines whether a signal belongs to the target investment universe.

This stage answers:

- Is this related to agent security at all?
- Is the company `core`, `adjacent`, or `out_of_scope`?
- Which category best describes it?

This prevents broad AI security or general agent companies from polluting the primary ranking.

### 3. Company Profile Layer

This is the center of the workflow.

Different sources may refer to the same company with different aliases. The workflow merges those signals into one company profile containing:

- canonical name
- aliases
- category
- evidence ledger
- score breakdown
- unknowns

This is the step that turns fragmented market noise into something an investor can reason about.

### 4. Evidence-Backed Scoring

Each profile is ranked using five dimensions:

- Team
- Market
- Business
- Tech
- Momentum

The point of the scoring system is not to produce fake precision. The point is to force the workflow to be explicit about why one company deserves attention before another.

### 5. Investor-Facing Output

The final output is a short list of candidate cards with:

- universe tier
- category
- score breakdown
- why now
- key evidence
- unknowns
- follow-up questions

This lets an investor decide where to spend the next 20 minutes of attention.

## Why This Workflow Is VC-Friendly

It maps directly onto how a research or investment team works:

- define target universe
- discover candidates
- collect evidence
- compare opportunities
- hand off the best names for analyst review

## Why The MVP Is Sufficient

A production system would add live ingestion, scheduling, and richer extraction. But for interview purposes, the critical proof is narrower:

> Can this sourcing workflow be clearly defined, made explainable, and demonstrated with a minimal executable prototype?

This MVP is designed to answer yes.
