# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Strategic priorities (the spine — work must ladder up to these)
1. [326f861414] Agentic synthesis's value in archaeology is not automating interpretation but drawing and enforcing the pattern-recognition / meaning-generation boundary — converting the discipline's already-existing, invisible, unquantified expert-judgment harms (false consensus, untracked inter-observer variation, Anglophone bias, taxonomic instability) into legible, quantified, auditable, queryable structure. The system structures dissent; it does not resolve it. This makes a correctly-bounded system materially safer than the untracked-judgment status quo, and locates the contribution in domain-led methodology (PECO schema, IOV protocols, observable/interpreted separation, versioned taxonomy-with-coherence) rather than commodity AI engineering.  ·ra-pm:thesis:ai-synthesis  [↑A001:AI2]
   ↳ seeded from ra-pm thesis

## Decisions
- Recall-biased prompt for intake triage written a priori from systematic-review screening best-practice, never by inspecting which papers were missed
- Prompt designed on Stewart (dev set), validated on Egeland and Harrison (held-out sets) with zero per-dataset tuning — generalization verified
- Accepted deliberate trade-off: lower noise rejection (60–68% vs API's 77–88%) in exchange for recall recovery at screening stage
- Three-stage cost architecture proven end-to-end: free intake triage (bound corpus) → free local recall-biased model (≥96% gold, offline, no data egress) → paid model only for interpretive core
- Testing qwen3:8b to evaluate whether a stronger free model can find the clean operating point gemma3 failed to achieve
- Classification benchmark uses gemma3:4b (free, local model) instead of API, tested on Stewart slice (337 gold + 400 non-gold), validated against API labels + gold retention
- Don't build paper theory on percolation—the elegant two-threshold theorem doesn't survive contact with data
- Reframe paper contribution from percolation theory to paragraph-level descriptive finding: complementary, anti-correlated channels explain why hybrid retrieval generalizes across domains
- Pipeline gaps are in evaluation and synthesis structure, NOT retrieval—LLM already wins on retrieval, so optimization efforts should not go there
- Capture-recapture is the highest-leverage addition: formalizes the headline finding ('gold standard is incomplete'), poetically fits extinction-review context, costs nearly nothing
- Will implement (in priority order): capture-recapture, percolation theory framing, argument frameworks for synthesis backbone; secondarily inter-rater stats (Krippendorff's α), graph community detection, entropy scoring for contestation
- exp02_guided_d2 experiment (PID 2950) is actively running, expected to produce next evaluation data
- Classifier is instructed to abstain (predict 'None') when a paper doesn't commit to a single cause — this behavior is by design, not a bug
- System should flag Mixed (ambiguous causation) cases to expert for judgment rather than auto-resolve them
- Redesign UI toward white background with negative space, editorial/minimal aesthetic
- Ground performance assessment in ra-pm brief and open issues rather than relying on memory
- Full-text coverage improved from 49 to 152/337 (45%) by using elsevier_tdm integration with API key + insttoken; team described as 'big win'
- Chose process-explicit macroecological modeling over correlative approaches because overreliance on correlative methods had been an obstacle to resolving extinction driver questions
- Integrated multiple independent data sources (modern/fossil records, ancient DNA, spatiotemporal climate reconstructions, species-specific population ecology, human expansion geography) to disentangle ecological mechanisms
- Snowball approach approval hinges on offline go/no-go test outcome: gold-peripheral must show higher outlink/inlink/coupling than noise-peripheral
- Literature synthesis pipeline sequence: topic→protocol→search→screen→appraise→extract→synthesize
- Search strategy uses PICO framework with wide/narrow screening and gray literature inclusion
- Porting meta-analysis toolkit from iDiv ecologists (Kambach/Ristok) into archaeology context as primary approach
- Read all documentation in the directory first (user emphasized 'I MEAN ALL OF them'), then conduct research, then write research brief(s)
- Build an AI, agentic, LLM-based world-class synthesis process; primary domain is archaeology, must be generalizable to other domains

## Constraints
- All validation based on held-out domains with zero role in prompt design (Stewart dev set is excluded from generalization claims)
- Citation giant-component is an upper bound on what one channel could reach, not the system's recall capacity
- Legibility and interpretability are non-negotiable; opaque methods (graph neural nets, neural rankers) would undermine the thesis, so must resist them
- Tool volume trajectory climbing while scope stable—may require architectural scaling of check gating
- Do not infer beyond the text.
- UI bug: clicking on responses or confidence numbers causes page to scroll back to top
- Semantic Scholar API has a hard rate limit of 1 request per second, cumulative across all endpoints
- Semantic Scholar API key must be sent in the x-api-key request header
- Accurate demographic reconstruction of muskox over 21,000 years requires high dispersal abilities, large maximum densities, and a small Allee effect
- We argue that given the accelerating speed of environmental change, NbS design for biodiversity recovery cannot be informed by past or current conditions but must create evolutionary potential for yet unknown future biodiversity.
- The results suggest that inquiline spiders (Arachnida) do not feed on termites directly, but on other invertebrates within the termitaria that are termitophagous, elevating the spiders three trophic levels higher than the termites.
- The femur and osteoderms were histologically sectioned, which has never been done for Gracilisuchidae.
- There are a variety of arguments involving the nature of species that purport to show that once they have disappeared they cannot be resurrected.
- Abstract: As the far-reaching consequences of human-generated climate change continue to threaten the earth, an evaluation of the historical narrative of the Anthropocene has never been more important.
- Some draw upon the structure of phylogenetic trees, some do not.
- Here, I argue that an individual flammable mutant genotype cannot invade the ‘group’ of non-flammable individuals because it implies unlikely patterns of seed dispersal and fitness advantages.
- Based on population structure, we do not discard the possibility that the fossil population was stable or in recovery, and/or was experiencing a high-predation period on younger individuals.
- The procedures are simple, rapid, involve no organic solvents and do not require multiple tube transfers for most types of samples.
- Our collective sense of " environmental consequences " has never been greater.
- In even the simplest foraging societies, people depend on a vast array of tools, detailed bodies of local knowledge, and complex social arrangements and often do not understand why these tools, beliefs, and behaviors are adaptive.
- The genus Scolia Fabricius, 1755 includes species that do not present diagnostic characters used to identify the other genera of Scoliini, and so it can be considered a "dumping ground group".
- Archaeological meta-analysis discipline lacks established protocols for systematic evidence synthesis
- Exercises directory is empty
- Next phase requires archaeology-specific documentation and remaining presentation decks
- Complete documentation review is a required prerequisite—blocking requirement before research phase begins

## Eliminations / rejected
- Percolation hypothesis ('citation giant-component predicts recall') falsified by empirical data: Stewart has highest recall (0.96) but lowest citation connectivity (0.73); Egeland/Harrison show inverse pattern (recall 0.81, connectivity 0.79–0.87)
- SPECTER embeddings tried and performed worse than baseline; embedding/neural retrieval is off the table
- Reject graph neural nets (opaque, kills contribution) and fine-tuning as not valuable for this work
- Prompt-strategy lever did not move eval recall from ~0.4 (n=8, noise floor)
- [4] Title: Emerging forests on abandoned land: Puerto Rico’s new forests
- Expert-sourcing bottleneck limits traditional approach to meta-analysis in archaeological field
- Part 4 - Literature Search.pdf and Altschul 2017 PDF processed; 4 decks + 5 literature files remain unread
- Conflicts are influenced by a growing human population and large mammal species re-colonising formerly abandoned areas.
- The habitation site was abandoned after the impact event and the site was buried within 200 years by alluvium.
- {"id": 7, "label": "skip", "confidence": 0.90, "reason": "Late Holocene impact; post-extinction, focuses on cultural abandonment"},
- Given the intensity of the survey, the scarcity of sampling is ruled out as the cause of this ‘palaeontological desert’.
- We examined biomarkers in dated sediment cores from two ponds adjacent to abandoned Thule settlements (PaJs-3 and PaJs-13) and compared these to sediment cores from two ponds without past human occupation.
- While not doing so could be our undoing, doing so could transform our collective consciousness into one that respects, nourishes, and embraces our interdependence with life on Earth.
- interior, mountains, vegetation, climate); presence versus absence of food production and movement into inhabited versus abandoned land have little impact on spread rates.
- Document-title-based searching rejected; source-location-based configuration is the acceptable approach
- Google Books unsuitable due to HTTP 429 rate-limiting on keyless requests
- Network expansion adds no additional value beyond uncapping retrieval; citation seeds already catch expansion targets
- Depth-3 rejected: cost-prohibitive, diminishing recall beyond 2-hop component, mostly adds noise outside tight component
- Unguided depth-2 rejected: cost-prohibitive and noise-dominated; classifier guidance required to keep corpus on-topic and bounded
- Initial assumption that 25-query set comprehensively covers PICO elements was rejected after audit revealed gaps
- 17 distinct approaches tested without changing score: different audit methodologies, source retrieval, hedging elimination, JSON-only output, prose output, and cited formats
- Nine rewriting iterations attempted without score change: direct quoting, explicit RQ-element mapping, reading Beast Mode Constitution, retrieving constitution file, changing scoring methodology, acknowledging task limitations
- Habitat modification and glacial shifts mechanisms not explicitly addressed in current queries
- Extirpation and range contraction outcomes not explicitly covered in current query set
- Eurasia proper was not addressed as an independent region in the 25-query set (only Beringia subregion included); missing from 6 named geographies

## Premises (provisional)
- Free local triage (qwen3:8b with recall-biased prompt) achieves ≥96% gold retention across all tested domains, matching or exceeding paid frontier API performance
- Despite this, current studies often assume that communities are structured by only a few key traits.
- Comparing whether qwen3:8b model finds a clean operating point that gemma3 could not (unconfirmed; pending run completion)
- gemma3 could not find a clean operating point
- Both test classifications correct: megafauna→core, CMOS chip→skip
- Stewart domain: weak citation connectivity (~4% of references on-topic, 73% of gold citation-linked) compensated by strong keyword retrieval (96%); Egeland/Harrison: strong citation connectivity (79–87%) but weaker keyword retrieval (81%, capped by terminology standardization)
- Citation search works and terminates at a phase-transition threshold—percolation theory explains this, providing principled bounds on when such search provably stops
- Pipeline and human review can be treated as independent 'nets' in capture-recapture logic to estimate true recall and papers both missed
- 1045 user prompts per 1217 sessions is unvalidated; need to confirm whether this represents sustained velocity or a temporary spike
- Projections that assume suitable habitat is limited to currently occupied biomes can produce underestimates of species viability.
- Two different pipelines were being conflated in the logs, explaining confusion about whether guided expansion reduced the 42K
- Guided pipeline recall verification is pending before proceeding with the reconciliation explanation
- Mixed classification is the interpretive boundary case where human meaning-generation does most work; this is the core thesis-relevant problem
- Non-Mixed classes achieve 74% accuracy (28/38); Mixed is the actual performance bottleneck, not overall architecture
- Rewritten JS validity and correspondence to stated intent requires verification against real numbers
- Prior work achieved very high precision and recall (unconfirmed memory; user plans to verify against ra-pm brief and issues)
- Climatic change was the primary driver of muskox distribution shifts (from validated process-explicit model projections; unconfirmed/not directly observable)
- In Canada and Greenland, climatic change and human activities probably combined as extinction drivers (unconfirmed; extraction confidence 0.72)
- Archaeological culture classification in CLIOARCH involves inter-observer variation and lumper/splitter debates that affect meta-analysis validity
- Riede et al. preprint is keystone reference using CLIOARCH database with 86 Named Archaeological Cultures
- Team is implementing megafauna extinction meta-analysis using metafor package in R
- Altschul et al. 2017 'Fostering Synthesis in Archaeology' established as foundational CfAS manifesto
- Borenstein, Koricheva, Gurevitch, Nakagawa, Foo already deeply known—no ramp-up needed
- Literature corpus: 5 presentation decks, 6 documents (1 already read), 3 case studies (Riede/Egeland/Buss), 1 R script, 1 WoS export
- Riede 2023 establishes anchor claim: archaeology lacks synthesis protocols
