"""What your code does with the distribution: threshold, abstain, escalate, combine."""
from __future__ import annotations

from .question import Answer, Question

THRESHOLD = 0.90   # act on the model only at or above this confidence


# --8<-- [start:dm-decide]
def decide(answer: Answer, question: Question, threshold: float = THRESHOLD) -> str:
    """Return the chosen option, "abstain" (refused), or "escalate" (not sure enough)."""
    if answer.refused:
        return "abstain"
    if not answer.probs or not all(0.0 <= p <= 1.0 for p in answer.probs.values()):
        # No distribution, an empty one, or a malformed one carries no confidence.
        return "escalate"
    best = max(question.options, key=lambda o: answer.probs.get(o, 0.0))
    return best if answer.probs.get(best, 0.0) >= threshold else "escalate"
# --8<-- [end:dm-decide]


# --8<-- [start:dm-combine]
def compliance_gate(client, listing: str, questions: list[Question]) -> str:
    """One predicate per independent factor, one request, combined here in code."""
    answers = client.decide_many(listing, questions)
    if not questions or len(answers) != len(questions):
        return "escalate"           # a missing judgment is never a pass
    outcomes = [decide(a, q) for a, q in zip(answers, questions)]
    if "true" in outcomes:          # any confident violation blocks the listing
        return "block"
    if all(o == "false" for o in outcomes):
        return "pass"
    return "escalate"               # an unsure or refused answer goes to a human
# --8<-- [end:dm-combine]
