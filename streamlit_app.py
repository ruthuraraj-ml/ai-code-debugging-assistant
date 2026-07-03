"""
Streamlit console for the Automated Code Debugging Crew.

Renders the four workflow artifacts (AnalysisReport, CorrectedCodeArtifact,
verification summary, RunMetrics/events) produced by DebuggingService. No
background threads or polling — the crew call is blocking, and the pipeline
strip is a post-hoc reconstruction from the recorded ExecutionEvents rather
than a live progress indicator.
"""

import difflib
import html
import json

import streamlit as st
from streamlit_ace import st_ace

from schemas.artifacts import SourceCodeArtifact
from schemas.enums import AgentRole, EventType, ExecutionOutcome, IssueSeverity
from services.debugging_service import DebuggingService


# =========================================================================
# Page config + theme
# =========================================================================

st.set_page_config(
    page_title="Code Debugging Console",
    page_icon="🛠️",
    layout="wide",
)

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --ink: #1E1E24;
    --ink-muted: #6B6B76;
    --surface: #FFFFFF;
    --surface-sunken: #F7F7FA;
    --border: #E4E4EB;
    --indigo: #4F46E5;
    --indigo-soft: #EEF0FD;
    --amber: #B45309;
    --amber-soft: #FEF3E2;
    --red: #B42318;
    --red-soft: #FEECEB;
    --coral: #C2410C;
    --coral-soft: #FEF0E6;
    --green: #15803D;
    --green-soft: #EAF7EE;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--ink);
}

code, pre, .mono {
    font-family: 'IBM Plex Mono', monospace !important;
}

h1, h2, h3 {
    font-weight: 600 !important;
    letter-spacing: -0.01em;
}

.app-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 0.25rem;
}
.app-subtitle {
    color: var(--ink-muted);
    font-size: 0.9rem;
    margin-top: -0.5rem;
    margin-bottom: 1.5rem;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}

.pipeline-strip {
    display: flex;
    gap: 8px;
    margin-bottom: 1.25rem;
}
.pipeline-stage {
    flex: 1;
    text-align: center;
    padding: 10px 6px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    background: var(--surface-sunken);
    color: var(--ink-muted);
    border: 1px solid var(--border);
}
.pipeline-stage.done {
    background: var(--indigo-soft);
    color: var(--indigo);
    border-color: var(--indigo);
}
.pipeline-stage.skipped {
    opacity: 0.5;
}

.metric-card {
    background: var(--surface-sunken);
    border-radius: 10px;
    padding: 0.9rem 1rem;
}
.metric-label {
    font-size: 0.8rem;
    color: var(--ink-muted);
    margin: 0 0 4px 0;
}
.metric-value {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0;
}

.badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 2px 9px;
    border-radius: 999px;
    text-transform: lowercase;
}
.badge-critical { background: var(--red-soft); color: var(--red); }
.badge-error    { background: var(--coral-soft); color: var(--coral); }
.badge-warning  { background: var(--amber-soft); color: var(--amber); }
.badge-info     { background: var(--indigo-soft); color: var(--indigo); }
.badge-category {
    background: var(--surface-sunken);
    color: var(--ink-muted);
    border: 1px solid var(--border);
}

.issue-card {
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.6rem;
}
.issue-title {
    font-weight: 500;
    font-size: 0.95rem;
    margin: 0 0 6px 0;
}
.issue-meta {
    color: var(--ink-muted);
    font-size: 0.8rem;
    margin: 0 0 6px 0;
}
.issue-fix {
    font-size: 0.85rem;
    color: var(--ink);
}

.diff-line {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    padding: 1px 8px;
    white-space: pre-wrap;
    border-radius: 3px;
}
.diff-add { background: var(--green-soft); color: #0F5C2E; }
.diff-del { background: var(--red-soft); color: var(--red); text-decoration: line-through; }
.diff-ctx { color: var(--ink-muted); }
.diff-empty { background: var(--surface-sunken); }

.diff-side-by-side { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.diff-header-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    background: var(--surface-sunken);
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--ink-muted);
    letter-spacing: 0.04em;
}
.diff-header-row > div { padding: 6px 10px; }
.diff-header-row > div:first-child { border-right: 1px solid var(--border); }
.diff-row { display: grid; grid-template-columns: 1fr 1fr; }
.diff-row > div:first-child { border-right: 1px solid var(--border); }

.exec-block {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    background: var(--surface-sunken);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    white-space: pre-wrap;
    max-height: 220px;
    overflow-y: auto;
}
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)


# =========================================================================
# Rendering helpers
# =========================================================================

SEVERITY_CLASS = {
    IssueSeverity.CRITICAL: "badge-critical",
    IssueSeverity.ERROR: "badge-error",
    IssueSeverity.WARNING: "badge-warning",
    IssueSeverity.INFO: "badge-info",
}

PIPELINE_STAGES = [
    (AgentRole.ANALYZER, "Analyzer"),
    (AgentRole.CORRECTOR, "Corrector"),
    (AgentRole.MANAGER, "Manager verification"),
]

AGENT_ICON = {"analyzer": "🔍", "corrector": "🛠", "manager": "✅"}
OUTCOME_ICON = {"success": "✓", "failure": "✗", "warning": "⚠", "skipped": "–"}


def severity_badge(severity) -> str:
    value = severity.value if hasattr(severity, "value") else str(severity)
    css_class = SEVERITY_CLASS.get(severity, "badge-info")
    return f'<span class="badge {css_class}">{html.escape(value)}</span>'


def category_badge(category) -> str:
    value = category.value if hasattr(category, "value") else str(category)
    return f'<span class="badge badge-category">{html.escape(value)}</span>'


def metric_card(label: str, value) -> str:
    return (
        '<div class="metric-card">'
        f'<p class="metric-label">{html.escape(label)}</p>'
        f'<p class="metric-value">{html.escape(str(value))}</p>'
        "</div>"
    )


def render_pipeline_strip(events) -> None:
    """
    Reconstructs which of the 3 real crew tasks (analyzer, corrector,
    manager) completed, from TASK_COMPLETED events emitted by the
    task_callback wired up in crew.py. This is a post-hoc render, not a
    live progress indicator — the crew call has already returned by the
    time this is drawn.
    """

    completed = {
        event.agent: event.duration_ms
        for event in events
        if event.event_type == EventType.TASK_COMPLETED.value
    }

    cols = st.columns(len(PIPELINE_STAGES))
    for col, (role, label) in zip(cols, PIPELINE_STAGES):
        duration = completed.get(role.value)
        is_done = role.value in completed
        state_class = "done" if is_done else "skipped"
        icon = "✓" if is_done else "–"
        duration_text = f" · {duration:.0f} ms" if duration is not None else ""
        col.markdown(
            f'<div class="pipeline-stage {state_class}">{icon} {html.escape(label)}{duration_text}</div>',
            unsafe_allow_html=True,
        )
    st.caption(
        "Each checkmark reflects one completed CrewAI task — not live progress."
    )


def render_diff(original: str, corrected: str) -> None:
    diff = difflib.ndiff(
        original.splitlines(keepends=False),
        corrected.splitlines(keepends=False),
    )

    rows = []
    for line in diff:
        tag, content = line[:2], line[2:]
        escaped = html.escape(content) if content.strip() else "&nbsp;"
        if tag == "+ ":
            rows.append(f'<div class="diff-line diff-add">+ {escaped}</div>')
        elif tag == "- ":
            rows.append(f'<div class="diff-line diff-del">- {escaped}</div>')
        elif tag == "  ":
            rows.append(f'<div class="diff-line diff-ctx">&nbsp; {escaped}</div>')
        # "? " intraline hint markers are dropped — too noisy for a console view.

    st.markdown("".join(rows), unsafe_allow_html=True)


def render_side_by_side_diff(original: str, corrected: str) -> None:
    """
    Two-column diff: original on the left, corrected on the right, aligned
    row by row using difflib.SequenceMatcher opcodes. Padding rows (blank,
    "diff-empty" background) keep the two sides in sync where lines were
    purely added or purely removed.
    """

    original_lines = original.splitlines()
    corrected_lines = corrected.splitlines()
    matcher = difflib.SequenceMatcher(None, original_lines, corrected_lines)

    def cell(text, css_class) -> str:
        escaped = html.escape(text) if text is not None else "&nbsp;"
        return f'<div class="diff-line {css_class}" style="border-radius:0;">{escaped}</div>'

    rows = [
        '<div class="diff-side-by-side">'
        '<div class="diff-header-row"><div>Original</div><div>Corrected</div></div>'
    ]

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        left_block = original_lines[i1:i2]
        right_block = corrected_lines[j1:j2]
        height = max(len(left_block), len(right_block), 1)

        for k in range(height):
            left = left_block[k] if k < len(left_block) else None
            right = right_block[k] if k < len(right_block) else None

            if tag == "equal":
                left_class, right_class = "diff-ctx", "diff-ctx"
            elif tag == "delete":
                left_class, right_class = "diff-del", "diff-empty"
            elif tag == "insert":
                left_class, right_class = "diff-empty", "diff-add"
            else:  # replace
                left_class = "diff-del" if left is not None else "diff-empty"
                right_class = "diff-add" if right is not None else "diff-empty"

            rows.append(
                '<div class="diff-row">'
                f"<div>{cell(left, left_class)}</div>"
                f"<div>{cell(right, right_class)}</div>"
                "</div>"
            )

    rows.append("</div>")
    st.markdown("".join(rows), unsafe_allow_html=True)


def render_execution_result(execution_result) -> None:
    if execution_result is None:
        st.caption("No execution result was recorded for this artifact.")
        return

    status = "success" if execution_result.success else "failed"
    st.markdown(
        f"**Execution:** {'ran' if execution_result.executed else 'not run'} "
        f"· **{status}**"
        + (
            f" · {execution_result.execution_time_ms:.1f} ms"
            if execution_result.execution_time_ms is not None
            else ""
        )
    )

    if execution_result.stdout:
        st.caption("stdout")
        st.markdown(
            f'<div class="exec-block">{html.escape(execution_result.stdout)}</div>',
            unsafe_allow_html=True,
        )
    if execution_result.stderr:
        st.caption("stderr")
        st.markdown(
            f'<div class="exec-block">{html.escape(execution_result.stderr)}</div>',
            unsafe_allow_html=True,
        )
    if execution_result.exception:
        st.caption("Exception")
        st.markdown(
            f'<div class="exec-block">{html.escape(execution_result.exception)}</div>',
            unsafe_allow_html=True,
        )

def render_event_table(events) -> None:
    """Icon-based event log — st.dataframe can't mix icons with structured data."""

    if not events:
        st.caption("No events recorded.")
        return

    rows = [
        '<table style="width:100%;font-size:0.85rem;border-collapse:collapse;">',
        '<tr style="color:var(--ink-muted);text-align:left;">'
        "<th style=\"padding:6px 8px;\">Agent</th><th>Event</th><th>Outcome</th>"
        '<th>Message</th><th style="text-align:right;">Duration</th></tr>',
    ]
    for event in events:
        agent_icon = AGENT_ICON.get(event.agent, "•")
        outcome_icon = OUTCOME_ICON.get(event.outcome, "•")
        duration = f"{event.duration_ms:.0f} ms" if event.duration_ms is not None else "–"
        rows.append(
            '<tr style="border-top:1px solid var(--border);">'
            f'<td style="padding:6px 8px;">{agent_icon} {html.escape(event.agent)}</td>'
            f"<td>{html.escape(event.event_type)}</td>"
            f"<td>{outcome_icon} {html.escape(event.outcome)}</td>"
            f"<td>{html.escape(event.message)}</td>"
            f'<td style="text-align:right;">{duration}</td>'
            "</tr>"
        )
    rows.append("</table>")
    st.markdown("".join(rows), unsafe_allow_html=True)


def build_report_markdown(analysis, correction, verification) -> str:
    lines = ["# Debugging report", ""]

    if analysis is not None:
        lines.append("## Analysis")
        if analysis.summary:
            lines.append(analysis.summary)
        lines.append(f"\n- Issues found: {analysis.total_issues}")
        lines.append(f"- Critical: {analysis.critical_issue_count}")
        for issue in analysis.issues:
            lines.append(
                f"\n### {issue.title} ({issue.severity}, line {issue.line_number or '–'})\n"
                f"{issue.details}"
            )
            if issue.suggested_fix:
                lines.append(f"\nSuggested fix: {issue.suggested_fix}")
        lines.append("")

    if correction is not None:
        lines.append("## Correction")
        if correction.modification_summary:
            lines.append(correction.modification_summary)
        lines.append(f"\nConfidence: {correction.correction_confidence:.2f}\n")
        lines.append("```python\n" + correction.corrected_source.source_code + "\n```")
        lines.append("")

    if verification:
        lines.append("## Verification")
        lines.append(verification)

    return "\n".join(lines)




if "result" not in st.session_state:
    st.session_state.result = None
if "source_code" not in st.session_state:
    st.session_state.source_code = (
        "def fibonacci(n):\n"
        "    if n = 0:\n"
        "        return 0\n"
    )


# =========================================================================
# Sidebar — source input
# =========================================================================

with st.sidebar:
    st.markdown(
        '<p style="font-size:1.05rem;font-weight:600;margin:0 0 2px;">Code debugging console</p>'
        '<p style="font-size:0.78rem;color:var(--ink-muted);margin:0 0 1rem;">'
        "analyzer → corrector → manager</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;'
        'letter-spacing:0.06em;color:var(--ink-muted);margin:0 0 6px;">'
        "PYTHON SOURCE</p>",
        unsafe_allow_html=True,
    )
    source_code = st_ace(
        value=st.session_state.source_code,
        language="python",
        theme="github",
        keybinding="vscode",
        font_size=13,
        tab_size=4,
        show_gutter=True,
        show_print_margin=False,
        wrap=False,
        auto_update=True,
        min_lines=20,
        max_lines=32,
        key="source_ace",
    )
    run_clicked = st.button("Analyze", type="primary", use_container_width=True)

if run_clicked:
    if not source_code.strip():
        st.sidebar.warning("Add some source code before starting a debugging run.")
    else:
        source = SourceCodeArtifact(run_id=None, source_code=source_code)
        with st.status("Running debugging crew...", expanded=True) as status:
            st.write("This can take a couple of minutes for the full sequential run.")
            service = DebuggingService()
            result = service.debug_code(source)
            status.update(label="Debugging run complete", state="complete")
        st.session_state.result = result
        st.session_state.source_code = source_code


# =========================================================================
# Results
# =========================================================================

result = st.session_state.result

if result is not None:
    analysis = result["analysis"]
    correction = result["correction"]
    verification = result["verification"]
    metrics = result["metrics"]
    events = result["events"]

    header_col, export_col, download_col = st.columns([4, 1, 1])
    header_col.markdown("#### Run results")
    export_col.download_button(
        "Export report",
        data=build_report_markdown(analysis, correction, verification),
        file_name="debugging_report.md",
        mime="text/markdown",
    )
    download_col.download_button(
        "Download trace",
        data=json.dumps(
            {
                "run_id": str(metrics.run_id),
                "metrics": metrics.model_dump(mode="json"),
                "events": [event.model_dump(mode="json") for event in events],
            },
            indent=2,
        ),
        file_name="trace.json",
        mime="application/json",
    )

    render_pipeline_strip(events)

    task_completions = {
        e.agent for e in events if e.event_type == EventType.TASK_COMPLETED.value
    }
    run_status = "completed" if len(task_completions) == len(PIPELINE_STAGES) else "incomplete"

    cols = st.columns(4)
    cols[0].markdown(metric_card("Run status", run_status.title()), unsafe_allow_html=True)
    cols[1].markdown(metric_card("Agents", len(task_completions) or len(PIPELINE_STAGES)), unsafe_allow_html=True)
    cols[2].markdown(
        metric_card("Issues found", analysis.total_issues if analysis is not None else "–"),
        unsafe_allow_html=True,
    )
    cols[3].markdown(
        metric_card("Issues fixed", correction.fixed_issue_count if correction is not None else "–"),
        unsafe_allow_html=True,
    )
    st.caption(f"Completed in {metrics.execution_time_ms / 1000:.1f}s")

    st.write("")

    tab_analysis, tab_corrected, tab_verification, tab_observability = st.tabs(
        ["Analysis", "Corrected code", "Verification", "Observability"]
    )

    # ---------------------------------------------------------------
    # Analysis tab -> AnalysisReport
    # ---------------------------------------------------------------
    with tab_analysis:
        if analysis is None:
            st.info("No AnalysisReport was returned for this run.")
        else:
            if analysis.summary:
                st.markdown(f"**Summary:** {analysis.summary}")
            if analysis.analysis_notes:
                st.caption(analysis.analysis_notes)

            with st.expander("Execution result", expanded=False):
                render_execution_result(analysis.execution_result)

            st.markdown("#### Issues")
            if not analysis.issues:
                st.success("No issues detected.")
            for issue in analysis.issues:
                st.markdown(
                    '<div class="issue-card">'
                    f'<p class="issue-title">{html.escape(issue.title)} '
                    f'{severity_badge(issue.severity)} {category_badge(issue.category)}</p>'
                    f'<p class="issue-meta">Line {issue.line_number or "–"}'
                    f'{f" · col {issue.column_number}" if issue.column_number else ""}</p>'
                    f'<p class="issue-fix">{html.escape(issue.details)}</p>'
                    + (
                        f'<p class="issue-fix"><b>Suggested fix:</b> {html.escape(issue.suggested_fix)}</p>'
                        if issue.suggested_fix
                        else ""
                    )
                    + "</div>",
                    unsafe_allow_html=True,
                )

    # ---------------------------------------------------------------
    # Corrected code tab -> CorrectedCodeArtifact
    # ---------------------------------------------------------------
    with tab_corrected:
        if correction is None:
            st.info("No CorrectedCodeArtifact was returned for this run.")
        else:
            if correction.modification_summary:
                st.markdown(f"**Modification summary:** {correction.modification_summary}")
            if correction.correction_notes:
                st.caption(correction.correction_notes)
            st.caption(f"Correction confidence: {correction.correction_confidence:.2f}")

            st.markdown("#### Original vs corrected")
            render_side_by_side_diff(
                st.session_state.source_code,
                correction.corrected_source.source_code,
            )

            with st.expander("Unified diff", expanded=False):
                render_diff(
                    st.session_state.source_code,
                    correction.corrected_source.source_code,
                )

            with st.expander("View corrected source", expanded=False):
                st.code(correction.corrected_source.source_code, language="python")

    # ---------------------------------------------------------------
    # Verification tab -> manager's raw output
    # ---------------------------------------------------------------
    with tab_verification:
        if not verification:
            st.info("No verification summary was returned for this run.")
        else:
            st.markdown(
                '<p style="font-weight:600;margin:0 0 4px;">Verification summary</p>'
                '<hr style="border:none;border-top:1px solid var(--border);margin:0 0 12px;">',
                unsafe_allow_html=True,
            )
            st.markdown(verification)
            st.caption(
                "Free-text output from the manager agent — not a structured "
                "checklist, since verification has no output_pydantic yet."
            )

    # ---------------------------------------------------------------
    # Observability tab -> RunMetrics + ExecutionEvents
    # ---------------------------------------------------------------
    with tab_observability:
        obs_cols = st.columns(4)
        obs_cols[0].markdown(metric_card("Total events", metrics.total_events), unsafe_allow_html=True)
        obs_cols[1].markdown(metric_card("Tool calls", metrics.tool_calls), unsafe_allow_html=True)
        obs_cols[2].markdown(metric_card("Issues found", metrics.issues_found), unsafe_allow_html=True)
        obs_cols[3].markdown(metric_card("Issues fixed", metrics.issues_fixed), unsafe_allow_html=True)

        st.write("")
        st.markdown("#### Event log")
        render_event_table(events)
else:
    st.markdown(
        '<div style="text-align:center;padding:4rem 1rem;color:var(--ink-muted);">'
        '<p style="font-size:1.1rem;font-weight:500;color:var(--ink);margin:0 0 6px;">'
        "🛠 Code debugging console</p>"
        "<p style=\"margin:0;\">Paste Python code in the sidebar, then click <b>Analyze</b>.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
