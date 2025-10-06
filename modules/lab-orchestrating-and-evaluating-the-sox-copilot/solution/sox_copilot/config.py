# Central knobs for teachability & stability
MODEL_NAME = "gpt-4o-mini"   # OpenAI chat model for both agent & narrative chain
MODEL_TEMP = 0.2             # Narrative chain (slight variance okay)
AGENT_TEMP = 0.0             # Tools-agent should be deterministic-ish
MAX_ITER = 3                 # Bound agent autonomy
AMOUNT_THRESHOLD = 1000.0    # PAY-002 threshold (can be changed in class)