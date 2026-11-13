# LangChain + Dataville MCP Quickstart

A ~60-line template for connecting a [LangChain](https://python.langchain.com)
agent to **Dataville** through its hosted MCP server. The agent can search live
SEC EDGAR filings and Wikipedia, and every answer comes back with the source
name and a URL you can check.

No scrapers, no ingestion pipeline, no vector database.

## What you'll build

The script connects to Dataville over MCP, discovers the available tools, builds
a LangChain agent with them, and answers one question:

```
Dataville tools: ['list_dataville_sources', 'search_dataville']

Tool call: search_dataville {'source': 'edgar', 'keywords': 'Nvidia 10-K'}

Answer:
...
```

The answer is trimmed here. Run it to see the full response.

## How it works

```text
main.py
  └─ MCPAdapter          connects to https://api.dataville.com/mcp
       └─ list_tools()   returns LangChain tools: list_dataville_sources, search_dataville
  └─ create_agent        gives those tools to a chat model
       └─ ainvoke()      the model calls Dataville, then writes the answer
```

MCP (Model Context Protocol) is a standard way for applications to expose tools
and data to LLM apps. Dataville hosts one MCP server that fronts all of its data
sources, so you connect once and get everything behind a consistent interface.

`langchain.mcp` is in beta. It wraps [FastMCP](https://gofastmcp.com) and turns
remote MCP tools into ordinary LangChain tools.

## Prerequisites

- Python 3.10 or later. Python 3.10–3.12 is the smoothest; 3.14 works but may
  print a Pydantic v1 compatibility warning.
- A tool-calling model and its provider key. The default uses OpenRouter
  (`anthropic/claude-sonnet-4-6`); Anthropic and OpenAI also work.
- Optional: a Dataville API key. Without one, requests use the anonymous
  allowance of **50 requests per 24 hours per IP address**.

## Quickstart

```bash
git clone https://github.com/datavilleorg/langchain-mcp-quickstart.git
cd langchain-mcp-quickstart

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

export OPENROUTER_API_KEY=YOUR_PROVIDER_KEY
export DATAVILLE_API_KEY=YOUR_DATAVILLE_KEY

python main.py
```

Get a Dataville key at <https://app.dataville.com/api-keys>. Leave
`DATAVILLE_API_KEY` unset to try it anonymously.

## What each part does

Everything is in `main.py`. The interesting pieces:

| Code | What it does |
| --- | --- |
| `config` | The `mcpServers` dict, pointing at `https://api.dataville.com/mcp`. It speaks streamable HTTP, so there is nothing to install or run locally. `auth` (optional) becomes an `Authorization: Bearer` header. |
| `SYSTEM_PROMPT` | The instructions passed to the agent. Edit it to change how the agent behaves. |
| `MCPAdapter(...)` | The connection. Used as an async context manager so it closes cleanly. |
| `list_tools()` | Returns Dataville's tools as LangChain tools, ready to pass to an agent. |
| `create_agent(...)` | Builds the agent from the model (`openrouter:anthropic/claude-sonnet-4-6`), the tools, and the system prompt. |
| `ainvoke(...)` | Runs one turn. The result keeps every message, including the tool calls. |
| tool-call loop | Prints what the agent asked Dataville for, so you can see the tool name and arguments. |

### The MCP config

This is the whole connection:

```python
config = {
    "mcpServers": {
        "dataville": {
            "url": "https://api.dataville.com/mcp",
            "auth": "dataville_...",   # optional
        }
    }
}
```

`mcpServers` maps a name to a server. `url` is required for a remote server and
`auth` is an optional bearer token.

> A trailing comma after the outer dict, like `config = { ... },`, turns the
> value into a one-item tuple and raises `ValueError: Could not infer a valid
> transport from: ({...},)`. Keep the closing brace bare.

## Dataville tools

| Tool | Arguments | Returns |
| --- | --- | --- |
| `list_dataville_sources` | none | The available source names and descriptions. |
| `search_dataville` | `source`, `keywords` | The single most relevant result from that source, including the source name, a URL, and structured metadata. |

For `edgar`, a company name or ticker returns its latest filing with that
period's financials and trailing-twelve-month figures. Add a form type such as
`10-K` or `10-Q` to the keywords to pick a specific filing.

## Data sources

`search_dataville` accepts these source names:

| Source | What it covers |
| --- | --- |
| `edgar` | SEC EDGAR company filings and financials, with TTM revenue, income, and capex |
| `wikipedia` | Wikipedia articles |
| `arxiv` | arXiv preprints |
| `census` | US Census Bureau data |
| `gutenberg` | Project Gutenberg public-domain books |
| `fooddata` | USDA FoodData Central |
| `paperswithcode` | Papers with Code: ML papers, code, and benchmarks |
| `news` | Front-page headlines from a historical archive (not live news) |
| `stackexchange` | Stack Exchange Q&A |
| `pypi` | PyPI package metadata |
| `openalex` | OpenAlex scholarly works |

## Example prompts

Copy one into the `content` string in `main.py`, or edit it in place:

```python
"content": "Summarize Nvidia's business from Wikipedia, then add its latest 10-K revenue and net income. Cite each source.",
```

More in [prompts/examples.md](prompts/examples.md), grouped by source.

## Using a different model provider

`init_chat_model` imports the provider package lazily, based on the model string
prefix. Install the package that matches your prefix and change the string in
`main.py`. You do not import the provider yourself.

**OpenRouter (default):**

```bash
pip install langchain-openrouter
export OPENROUTER_API_KEY=...
```

```python
init_chat_model("openrouter:anthropic/claude-sonnet-4-6", temperature=0)
```

**Anthropic directly:**

```bash
pip install langchain-anthropic
export ANTHROPIC_API_KEY=...
```

```python
init_chat_model("anthropic:claude-sonnet-5", temperature=0)
```

**OpenAI:**

```bash
pip install langchain-openai
export OPENAI_API_KEY=...
```

```python
init_chat_model("openai:gpt-5", temperature=0)
```

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `ValueError: Could not infer a valid transport from: ({...},)` | A trailing comma after the outer `config` dict made it a tuple. Remove the comma. |
| `ImportError: ... requires the langchain-openrouter package` | Install the provider package named in the error (or switch the model string prefix to one you have). |
| `429` with a limit of 50 | You are on the anonymous allowance. Set `DATAVILLE_API_KEY` and rerun. |
| The agent never calls Dataville | The model does not support tool calling, or the model string has no provider prefix. Use a tool-calling model such as `openrouter:anthropic/claude-sonnet-4-6`. |
| A result says the data is stale | Dataville served a stored copy while the upstream was unavailable. Rerun later. |

## Learn more

- Docs: <https://docs.dataville.com>
- Connect an AI tool (MCP): <https://docs.dataville.com/ai-tools#langchain>
- Response format: <https://docs.dataville.com/response-format>
- MCP server repo: <https://github.com/datavilleorg/dataville-mcp>
- API keys: <https://app.dataville.com/api-keys>

## License

MIT. See [LICENSE](LICENSE).
