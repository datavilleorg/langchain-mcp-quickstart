# Example prompts

Copy one of these into the `content` string in `main.py`.

## SEC EDGAR (filings and financials)

- `Use Dataville to find Nvidia's latest 10-K filing and summarize revenue and net income.`
- `What did Apple report for revenue and net income in its most recent 10-Q?`
- `Find Microsoft's latest 8-K and summarize what it announced.`
- `Compare the latest 10-K revenue for Nvidia and AMD.`

The last one makes two `edgar` calls. Include a form type such as `10-K` or
`10-Q` when you need a specific filing; otherwise the tool returns the most
recent filing of any form.

## Wikipedia (background and provenance)

- `Use Dataville to summarize Anthropic's history from Wikipedia, with a source link.`
- `What is the Wikipedia summary of the Apollo 11 mission? Cite the article URL.`

## Cross-dataset

- `Summarize Nvidia's business from Wikipedia, then add its latest 10-K revenue and net income. Keep the two sources separate and cite each.`
- `Give me a one-paragraph company snapshot of Apple using Wikipedia for background and SEC EDGAR for the latest financials.`

## Other sources

- arXiv: `Find recent arXiv papers about retrieval-augmented generation.`
- PyPI: `What is the latest PyPI metadata for the langchain package?`
- Stack Exchange: `Find a Stack Exchange answer about Python asyncio.`
- Census: `Look up US Census data for population.`
- OpenAlex: `Find scholarly works on graph neural networks.`
- FoodData: `Look up nutrition data for almonds.`
- Papers with Code: `Find benchmarks for image classification.`
- Gutenberg: `Find a Project Gutenberg book by Jane Austen.`
- News: `Show front-page headlines about space exploration from the news archive.`

The news source is a historical archive of front-page headlines, not live news.

## Notes

- `search_dataville` returns the single most relevant result per call, not a
  paginated feed. Ask for one thing at a time, or let the agent make several
  calls.
- The agent can call `list_dataville_sources` to discover source names at
  runtime.
