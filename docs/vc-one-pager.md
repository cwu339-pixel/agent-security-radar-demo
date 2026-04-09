# VC One-Pager

## Problem

An investment team tracking agent security companies faces four recurring problems:

- the target universe is poorly defined
- new companies are discovered too late or inconsistently
- evidence is fragmented across many sources
- analyst attention is wasted on low-priority names

The question is not “can we search the web?” The question is:

> How do we turn noisy public signals into an explainable, investor-ready short list?

## Why Now

Agent security is emerging as a distinct area within AI infrastructure and enterprise security. As agents gain tool access, memory, permissions, and external execution capabilities, new company categories are appearing around:

- runtime controls
- prompt and tool injection defense
- policy enforcement
- identity and access for agents
- observability and audit
- sandboxing and containment

This creates a sourcing problem: relevant companies can appear in social posts, hiring pages, product blogs, open source repos, databases, and research long before they become obvious market leaders.

## What The System Does For Investors

This system is designed to support a VC workflow, not just summarize content.

It helps an investment team:

- define what belongs in the agent security universe
- continuously surface new candidate companies
- merge fragmented evidence into one company profile
- rank opportunities using an explainable rubric
- hand analysts a short list with `why now`, `unknowns`, and `follow-up questions`

## What The MVP Proves

The MVP does not use live data. Instead, it proves the logic of the workflow:

- representative signals can be normalized
- company aliases can be merged
- names can be labeled as `core`, `adjacent`, or `out_of_scope`
- candidate cards can be generated in an investment-friendly format

## What Remains Intentionally Out Of Scope

This package intentionally does not include:

- live crawling of paid or restricted sources
- 24x7 orchestration
- live model-based extraction
- CRM integration
- a production dashboard

Those are implementation extensions. The interview objective here is to prove that the workflow design is coherent and useful for a VC team.
