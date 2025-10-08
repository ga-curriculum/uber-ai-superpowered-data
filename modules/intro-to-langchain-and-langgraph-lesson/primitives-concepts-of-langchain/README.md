<h1>
  <span>

  ![alt text](../assets/ga-logo.png)

  </span>
  <span class="subhead">Primitives & Concepts of LangChain</span>
</h1>

**Learning objective:** Explain the core primitives of LangChain and demonstrate how they compose into functional LLM applications for rapid prototyping.

## The Core Primitives

### 1. Prompts & Prompt Templates

A **prompt template** is a reusable template for generating prompts with variables. Instead of hardcoding strings, you create templates that can be filled in dynamically.

Key characteristics:

- Parameterized text with placeholders for variables
- Enables consistent prompt formatting across your application
- Supports multiple input variables
- Can include few-shot examples and system messages

**Why it matters:**

Raw string formatting is error-prone and hard to maintain. Prompt templates make your prompts reusable, testable, and version-controlled.

**Code example:**

```python
from langchain.prompts import PromptTemplate

# Simple template
template = """You are a financial auditor. Analyze the following control:

Control ID: {control_id}
Control Description: {description}

Provide your assessment of whether this control is functioning effectively."""

prompt = PromptTemplate(
    input_variables=["control_id", "description"],
    template=template
)

# Use it
formatted_prompt = prompt.format(
    control_id="AC-001",
    description="Access to financial systems requires MFA"
)
```

---

### 2. LLMs & Chat Models

The **LLM** and **ChatModel** are wrappers around language model APIs that provide a consistent interface regardless of provider.

Types:

- **LLM**: Text-in, text-out (completion models)
- **ChatModel**: Messages-in, message-out (chat-based models like GPT-4)

Key characteristics:

- Provider-agnostic interface (switch between OpenAI, Anthropic, etc.)
- Built-in retry logic and error handling
- Support for streaming responses
- Token counting and cost tracking

**Code example:**

```python
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Initialize model
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Use with messages
messages = [
    SystemMessage(content="You are a financial compliance expert."),
    HumanMessage(content="Explain SOX 404 requirements in simple terms.")
]

response = llm.invoke(messages)
print(response.content)
```

---

### 3. Chains

A **chain** is a sequence of calls to LLMs, prompts, or other components. Chains are the fundamental building block of LangChain applications.

Types of chains:

- **LLMChain**: Prompt + LLM (most basic)
- **SequentialChain**: Multiple chains in sequence
- **RouterChain**: Routes to different chains based on input
- **TransformChain**: Applies transformations to data

Key characteristics:

- Composable - chains can contain other chains
- Linear execution flow (mostly)
- Implicit state passing between steps
- Quick to prototype with

**Code example:**

```python
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Create prompt
prompt = PromptTemplate(
    input_variables=["control_description"],
    template="Assess this control for effectiveness: {control_description}"
)

# Create chain
llm = ChatOpenAI(temperature=0)
chain = LLMChain(llm=llm, prompt=prompt)

# Run it
result = chain.invoke({
    "control_description": "All wire transfers require dual approval"
})

print(result["text"])
```

---

### 4. Tools & Agents

**Tools** are functions that an LLM can call, and **Agents** use LLMs to decide which tools to call and in what order.

Key characteristics:

- Tools extend LLM capabilities (search, calculators, APIs, databases)
- Agents use ReAct (Reasoning + Acting) pattern
- Can create dynamic workflows based on LLM decisions
- Introduces non-determinism (agent decides the path)

Types of agents:

- **Zero-shot ReAct**: Decides tools based only on descriptions
- **Conversational**: With memory for chat-like interaction
- **OpenAI Functions**: Uses function calling API

**Code example:**

```python
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

# Define custom tool
def search_controls(query: str) -> str:
    """Search control database for relevant controls"""
    # In reality, this would query your database
    return f"Found 3 controls matching '{query}'"

tools = [
    Tool(
        name="ControlSearch",
        func=search_controls,
        description="Search for financial controls by keyword"
    )
]

# Create agent
llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Agent decides whether to use tool
result = agent.invoke("Find all controls related to wire transfers")
```

---

### 5. Output Parsers

**Output parsers** structure the LLM's text output into usable data formats like JSON, lists, or custom objects.

Key characteristics:

- Transform unstructured text into structured data
- Include retry logic for malformed outputs
- Support validation and error correction
- Critical for integrating LLM outputs into downstream systems

Types:

- **StructuredOutputParser**: Parse to dictionary with defined fields
- **PydanticOutputParser**: Parse to Pydantic models
- **JSONOutputParser**: Parse to JSON
- **ListOutputParser**: Parse to lists

**Code example:**

```python
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Define output structure
class ControlAssessment(BaseModel):
    control_id: str = Field(description="The control identifier")
    effectiveness: str = Field(description="Effective or Ineffective")
    risk_level: str = Field(description="High, Medium, or Low")
    recommendation: str = Field(description="Auditor recommendation")

# Create parser
parser = PydanticOutputParser(pydantic_object=ControlAssessment)

# Prompt with format instructions
prompt = PromptTemplate(
    template="Assess this control:\n{control}\n{format_instructions}",
    input_variables=["control"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Chain it together
llm = ChatOpenAI(temperature=0)
chain = prompt | llm | parser

result = chain.invoke({
    "control": "All journal entries require manager approval"
})

# Result is a typed Python object
print(result.effectiveness)
print(result.risk_level)
```

---

## How Primitives Compose

Here's how these primitives work together in a typical LangChain application:

```
┌──────────────┐
│    Input     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Prompt     │──► Format with variables
│  Template    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     LLM      │──► Generate response
│   / Model    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Output     │──► Structure the output
│   Parser     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Result    │
└──────────────┘
```

---

## Strengths & Limitations

| Aspect | Strengths | Limitations |
|--------|-----------|-------------|
| **Speed** | Rapid prototyping, minimal boilerplate | Can become messy at scale |
| **Abstractions** | Clean APIs, provider-agnostic | Hides some complexity that you may need |
| **State** | Simple passing between chain steps | No explicit state management |
| **Routing** | Basic with RouterChain | Limited conditional logic |
| **Error Handling** | Built-in retries for API calls | No structured error recovery patterns |
| **Debugging** | Verbose mode shows steps | Hard to inspect intermediate state |
| **Testing** | Can mock LLM calls | Chains can be hard to unit test |
| **Auditability** | Can log chain runs | No built-in execution trace |

💡 **Key insight**: LangChain is optimized for developer velocity, not production robustness.

---


---

## When LangChain Isn't Enough

As applications grow, you'll hit these walls:

❌ **No explicit state management** → hard to debug multi-step workflows  
❌ **Limited error recovery** → chains fail fast without graceful handling  
❌ **Linear execution model** → can't easily represent complex branching logic  
❌ **Implicit data flow** → state is passed implicitly, making audits difficult  
❌ **Hard to test** → chains are tightly coupled, making unit tests challenging  

💡 This is where **LangGraph** comes in — the next lesson will show you how graphs solve these problems.

---

<aside style="background-color:#2a2a2a; padding: 1.33rem 2rem .33rem; border-radius: .5rem">

## Key Takeaway

LangChain gives you **5 essential primitives** to build LLM applications:

1. **Prompts** → Reusable templates
2. **LLMs** → Model interface
3. **Chains** → Sequential logic
4. **Tools/Agents** → External capabilities
5. **Output Parsers** → Structured results


</aside>