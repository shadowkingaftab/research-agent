# --- Cognitive Loop Schemas ---
class InitialCognitivePlan(BaseModel):
    objective: str = Field(description="The deep, inferred research objective.")
    initial_knowns: List[str] = Field(description="Facts or context already known about the topic.")
    initial_unknowns: List[str] = Field(description="Specific information gaps that must be resolved.")

class CognitiveDecision(BaseModel):
    updated_knowns: List[str] = Field(description="Comprehensive list of all verified facts known so far.")
    updated_unknowns: List[str] = Field(description="Remaining specific information gaps.")
    thought: str = Field(description="Reasoning about the current epistemic gap and why the chosen action is the highest value.")
    tool: str = Field(pattern="^(search|crawl|extract|validate|build_kg|review|write|finish)$")
    search_focus: str = Field(default="", description="If searching, the exact specific question or concept to resolve an unknown.")
    boundary_reached: bool = Field(default=False, description="True if the objective cannot be further satisfied.")
    boundary_justification: str = Field(default="", description="If boundary_reached is True, explain why.")


# --- Search Strategy Schemas ---
class StrategyHypothesis(BaseModel):
    id: str = Field(description="Unique identifier for the hypothesis, e.g., H1, H2.")
    description: str = Field(description="What this hypothesis attempts to prove or find.")
    target_unknown: str = Field(description="Which specific unknown gap this addresses.")

class StrategyDecision(BaseModel):
    hypotheses: List[StrategyHypothesis] = Field(description="1-3 distinct search hypotheses.")
    selected_modalities: List[str] = Field(description="Target sources: web, github, scholar, news, company_websites, official_docs, etc.")
    queries: List[str] = Field(description="2-4 highly specific, non-repetitive search queries.")
    reasoning: str = Field(description="Brief explanation of the strategy and why these modalities/queries were chosen.")