import json

import streamlit as st

from core.task import Task
from core.agent_engine import agent_engine
from core.logger import logger
from core.research_memory import research_memory
from exporters.markdown_exporter import MarkdownExporter
from exporters.json_exporter import JSONExporter

st.set_page_config(
    page_title="Research Agent",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Research Agent")

# ---------------------------------
# Sidebar: Project selection (Research Memory)
# ---------------------------------

st.sidebar.header("Project")

existing_projects = sorted(
    p.stem for p in research_memory.memory_dir.glob("*.json")
)

project_choice = st.sidebar.selectbox(
    "Reuse existing project memory",
    options=["(new project)"] + existing_projects,
)

new_project_name = ""

if project_choice == "(new project)":
    new_project_name = st.sidebar.text_input(
        "New project name (optional)",
        placeholder="e.g. ai_companies_europe",
    )

use_memory = st.sidebar.checkbox("Use Research Memory", value=True)

if project_choice != "(new project)":
    st.sidebar.caption(
        f"Will load prior evidence from project: **{project_choice}**"
    )

# ---------------------------------
# Chat history
# ---------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_task" not in st.session_state:
    st.session_state.last_task = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask me anything...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        status = st.empty()
        status.info("🔍 Researching...")

        logger.clear()

        task = Task(user_request=prompt)

        task.use_memory = use_memory

        if project_choice != "(new project)":
            task.project_name = project_choice
        elif new_project_name.strip():
            task.project_name = new_project_name.strip()

        try:
            agent_engine.run(task)

            status.success("✅ Research complete.")

            response = task.final_answer or "No final answer generated."

            st.markdown(response)

            st.session_state.last_task = task

        except Exception as e:

            response = f"Error:\n\n{e}"

            status.error("❌ Research failed.")
            st.code(str(e))

            st.session_state.last_task = task

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

# ---------------------------------
# Result details for the most recent run
# ---------------------------------

task = st.session_state.last_task

if task is not None:

    st.divider()
    st.subheader("Run Details")

    stats = getattr(task, "research_statistics", {}) or {}

    cols = st.columns(4)

    cols[0].metric("Documents", stats.get("documents", 0))
    cols[1].metric("Evidence Items", stats.get("evidence_total", 0))
    cols[2].metric("Memory Hits", stats.get("memory_hits", getattr(task, "memory_hits", 0)))
    retrieved = getattr(task, "retrieved_evidence", [])

    cols[3].metric(
        "Evidence Used in Report",
        len(retrieved),
    )

    if stats.get("evidence_by_category"):
        st.caption("Evidence by category")
        st.json(stats["evidence_by_category"])

    # ---------------------------------
    # Knowledge Graph (Mermaid)
    # ---------------------------------

    task_data = getattr(task, "data", {})

    mermaid = task_data.get(
        "knowledge_graph_mermaid",
        "",
    )

    if mermaid:

        st.subheader("Knowledge Graph")

        mermaid_code = mermaid.strip("`").replace("mermaid\n", "", 1)

        st.components.v1.html(
            f"""
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
            <div class="mermaid">{mermaid_code}</div>
            <script>mermaid.initialize({{ startOnLoad: true }});</script>
            """,
            height=500,
            scrolling=True,
        )

    # ---------------------------------
    # Contradictions
    # ---------------------------------

    contradictions = task_data.get(
        "contradictions",
        [],
    )

    if contradictions:

        with st.expander(f"⚠️ {len(contradictions)} possible contradiction(s)"):

            for c in contradictions[:20]:
                st.markdown(
                    f"- **[{c['severity']}]** "
                    f"\"{c['evidence_a'].fact}\" vs \"{c['evidence_b'].fact}\""
                )

    # ---------------------------------
    # Progress / Logs
    # ---------------------------------

    with st.expander("Research progress / logs"):
        st.code("\n".join(logger.entries), language="text")

    # ---------------------------------
    # Downloads
    # ---------------------------------

    st.subheader("Downloads")

    dl_cols = st.columns(2)

    if task.final_answer:

        dl_cols[0].download_button(
            "Download Markdown Report",
            data=task.final_answer,
            file_name=f"{MarkdownExporter().safe_filename(
                             getattr(task, "goal", "") or "report"
                         )}.md",
            mime="text/markdown",
        )

    json_exporter = JSONExporter()

    json_payload = json.dumps(
        json_exporter._serialize(
            {
                "goal": task.goal,
                "user_request": task.user_request,
                "final_answer": task.final_answer,
                "evidence": task.extracted_data,
                "retrieved_evidence": getattr(
                    task,
                    "retrieved_evidence",
                    [],
                ),
                "research_statistics": task.research_statistics,
                "knowledge_graph": task_data.get(
                    "knowledge_graph",
                    {},
                ),
            }
        ),
        indent=2,
        ensure_ascii=False,
    )

    dl_cols[1].download_button(
        "Download JSON",
        data=json_payload,
        file_name=f"{MarkdownExporter().safe_filename(
                         getattr(task, "goal", "") or "report"
                     )}.json",
        mime="application/json",
    )