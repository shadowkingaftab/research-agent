from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class CognitiveState:
    objective: str = ""
    knowns: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    current_focus: str = ""
    epistemic_boundary_reached: bool = False
    boundary_justification: str = ""
    confidence_score: float = 0.0
    loop_iterations: int = 0
    max_iterations: int = 20  # Safety limit for the cognitive loop

    def is_satisfied(self) -> bool:
        """Determines if the research objective has been met."""
        if self.epistemic_boundary_reached:
            return True
        if self.loop_iterations >= self.max_iterations:
            return True
        # Satisfied if no critical unknowns remain and confidence is high
        return len(self.unknowns) == 0 and self.confidence_score >= 0.85

    def update_from_brain(self, knowns: List[str], unknowns: List[str], 
                          confidence: float, boundary_reached: bool, boundary_reason: str):
        self.knowns = knowns
        self.unknowns = unknowns
        self.confidence_score = confidence
        self.epistemic_boundary_reached = boundary_reached
        self.boundary_justification = boundary_reason
        self.loop_iterations += 1