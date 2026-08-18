# RAG Architecture Guide

Decision guide for designing Retrieval-Augmented Generation systems.
**Use in**: Phase 4 — ML Architecture & Pipeline Design

---

## RAG vs. Fine-Tuning Decision Matrix

Start here. Choose the right approach before designing anything.

| Factor | Favors RAG | Favors Fine-Tuning |
|--------|-----------|-------------------|
| Data volume | < 10K documents | > 100K labeled examples |
| Update frequency | Frequent (daily / weekly) | Rare (monthly+) |
| Explainability need | High — need source citations | Low |
| Domain specificity | Moderate | Very high / specialized vocabulary |
| Latency budget | Moderate (retrieval adds 100–300ms) | Tight (< 100ms) |
| Hallucination tolerance | Low — grounded answers required | Moderate |

**Default**: Start with RAG. Move to fine-tuning only when RAG's retrieval ceiling is reached and you have sufficient labeled data.

---

## Chunking Strategy Selection

| Strategy | Best For | Chunk Size | Overlap |
|----------|----------|-----------|---------|
| Fixed-size | General text, logs | 256–512 tokens | 10–20% |
| Sentence-based | Q&A, conversational | 3–5 sentences | 1 sentence |
| Paragraph-based | Structured documents | Natural paragraphs | None |
| Semantic | Mixed content types | Variable by topic | None |
| Document-level | Short documents (< 1 page) | Full document | N/A |
| Hierarchical | Long documents | Parent + child chunks | Parent context |

**Decision flow**:
1. Short documents (< 512 tokens)? → Document-level
2. Highly structured with headers/sections? → Semantic or paragraph-based
3. Conversational or Q&A? → Sentence-based
4. Long unstructured text? → Fixed-size with overlap
5. Mixed content types? → Hierarchical (parent-child)

---

## Embedding Model Selection

| Model | Strengths | Weaknesses | Use When |
|-------|-----------|------------|----------|
| OpenAI text-embedding-3-large | High quality, easy API | Cost, vendor lock-in | General purpose, fast start |
| Cohere Embed v3 | Multilingual, compression | API dependency | Multilingual content |
| BGE / E5 (open source) | Free, self-hosted | Requires infrastructure | Privacy-sensitive, high volume |
| Domain fine-tuned | Best domain accuracy | Requires training data | Specialized vocabulary |

**Selection criteria**:
- Privacy constraints → Self-hosted open-source
- Multilingual content → Cohere or multilingual fine-tuned
- Cost sensitivity → Open-source with quantization
- Maximum quality → Largest model within latency budget

---

## Retrieval Method Selection

| Method | How It Works | Strengths | Weaknesses |
|--------|-------------|-----------|------------|
| Dense (vector) | Embed query + cosine similarity | Semantic understanding | Misses exact keyword matches |
| Sparse (BM25 / TF-IDF) | Keyword matching | Exact term matches | No semantic understanding |
| Hybrid | Dense + Sparse combined | Best of both | More complex, needs tuning |
| Reranking | Retrieve broad, rerank narrow | Higher precision | Adds 50–100ms latency |

**Recommended default for production**: Hybrid retrieval + reranking

```
Query
  → Dense retrieval (top 20) + Sparse retrieval (top 20)
  → Merge + deduplicate (top 30)
  → Reranker (top 5–10)
  → LLM generation with grounded context
```

---

## Context Window Management

| Strategy | When to Use |
|----------|-------------|
| Stuff all chunks | Total context < 50% of model window |
| Map-reduce | Many chunks, need comprehensive synthesis |
| Refine | Sequential processing, building on prior answers |
| Compression | Context exceeds window, all sources needed |

**Rule of thumb**: Keep retrieved context below 50% of the model's context window.
Leave room for system prompt, query, and generation.

---

## Caching Strategy

| Cache Layer | What to Cache | TTL | When to Use |
|-------------|---------------|-----|-------------|
| Embedding cache | Query → vector | 24h | High query volume |
| Retrieval cache | Query → retrieved chunks | 1–4h | Repeated queries |
| Response cache | Query → full response | 15min–1h | Identical queries |
| Semantic cache | Similar queries → response | 1h | Paraphrased queries |

---

## Evaluation Metrics

### Retrieval Quality

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| Recall@K | Relevant docs in top K | > 0.85 |
| MRR (Mean Reciprocal Rank) | Rank of first relevant result | > 0.70 |
| NDCG@K | Ranking quality | > 0.75 |

### Generation Quality

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| Groundedness | Answer supported by retrieved sources | > 0.90 |
| Faithfulness | No claims beyond the sources | > 0.90 |
| Relevance | Answer addresses the query | > 0.85 |
| Completeness | All relevant info from sources included | > 0.80 |

### End-to-End

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| Answer accuracy | Correct answers | > 0.85 |
| Hallucination rate | Unsupported claims | < 0.05 |
| Latency P95 | Response time end-to-end | < 3s |
| Empty retrieval rate | Queries with no results | < 0.10 |

**Note**: Evaluate retrieval and generation separately first. Combined metrics hide where failures originate.

---

## Production Monitoring for RAG

Once deployed, monitor these signals continuously.

**Reference**: `monitoring-setup-guide.md` → Section 3 (RAG Quality Signals)

Key signals:
- Retrieval relevance score (alert if drops below 0.70)
- Empty retrieval rate (alert if > 10%)
- Hallucination rate (alert if > 5%)
- Index freshness (alert if index not updated within SLA)

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Chunks too large → diluted relevance | Start at 256–512 tokens, tune up only with evidence |
| Chunks too small → lost context | Include overlap, test with real production queries |
| No reranking → noisy context | Always rerank in production |
| Evaluating only end-to-end → optimizing blind | Measure retrieval and generation separately |
| Single embedding model | Evaluate 2–3 models on domain data before committing |
| No caching → high latency and cost | Cache at every layer where staleness is acceptable |

---

**Cross-references**:
- `SKILL.md` — Phase 4 RAG vs. Fine-tuning decision, Phase 5 prompt engineering
- `monitoring-setup-guide.md` — RAG Quality Signals (Section 3)
- `prompt-testing-patterns.md` — Testing prompts used in RAG generation step
- `model-card-template.md` — Document RAG architecture decisions
