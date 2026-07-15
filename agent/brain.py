from core.llm import llm


def decide(task):

    thoughts = "\n".join(
        task.thoughts[-10:]
    ) if getattr(task, "thoughts", None) else "None"

    action_history = getattr(
        task,
        "action_history",
        [],
    )

    recent_actions = "\n".join(
        f"- Step {a.get('step', '?')}: {a.get('tool', '')}"
        for a in action_history[-10:]
    ) or "None"

    allowed_tools = getattr(
        task,
        "tools",
        [
            "search",
            "crawl",
            "extract",
            "merge",
            "validate",
            "write",
            "finish",
        ],
    )

    evidence_summary = []

    for evidence in getattr(task, "extracted_data", [])[:20]:

        try:

            evidence_summary.append(
                f"- [{evidence.category}] "
                f"{evidence.fact} "
                f"(confidence={evidence.confidence:.2f})"
            )

        except Exception:

            evidence_summary.append(str(evidence))

    evidence_text = (
        "\n".join(evidence_summary)
        if evidence_summary
        else "None"
    )

    prompt = f"""
You are the reasoning engine of an autonomous research agent.

Your job is to decide the SINGLE best next action.

GOAL
----------------
{task.goal}

USER REQUEST
----------------
{task.user_request}

CURRENT STATE
----------------

Search Queries:
{task.search_queries}

Documents Collected:
{len(task.documents)}

Research Corpus Length:
{len(task.research_corpus)}

Evidence Summary:
{evidence_text}

Previous Thoughts:
{thoughts}

Recent Actions:
{recent_actions}

AVAILABLE TOOLS
----------------
{chr(10).join(allowed_tools)}

RULES
----------------
1. Search before crawling.
2. Crawl before extracting.
3. Extract before merging.
4. Merge before writing.
5. Only finish after writing.
6. Never repeat unnecessary actions.
7. Only choose tools from the AVAILABLE TOOLS list.
8. If more research is needed, search again.

Return ONLY valid JSON.

{{
    "thought": "...",
    "tool": "search"
}}
"""

    try:

        decision = llm.generate_json(prompt)

        if not isinstance(decision, dict):
            raise ValueError("Decision is not a JSON object.")

        tool = decision.get("tool", "search")

        if tool not in allowed_tools:
            tool = "search"

        return {
            "thought": decision.get(
                "thought",
                "Continuing research.",
            ),
            "tool": tool,
        }

    except Exception:

        if "search" in allowed_tools:
            fallback_tool = "search"
        elif "write" in allowed_tools:
            fallback_tool = "write"
        else:
            fallback_tool = allowed_tools[0]

        return {
            "thought": "Planner fallback after reasoning failure.",
            "tool": fallback_tool,
        }