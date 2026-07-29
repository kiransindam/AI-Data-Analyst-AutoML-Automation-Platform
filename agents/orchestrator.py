# agents/orchestrator.py
from typing import Dict, Any, TypedDict, Annotated
from langgraph.graph import StateGraph, END
import logging

from agents.data_understanding_agent import DataUnderstandingAgent
from agents.data_cleaning_agent import DataCleaningAgent
from agents.eda_agent import EDAAgent
from agents.insight_agent import InsightAgent
from agents.ml_decision_agent import MLDecisionAgent
from agents.model_training_agent import ModelTrainingAgent
from agents.evaluation_agent import EvaluationAgent
from agents.report_agent import ReportAgent

logger = logging.getLogger(__name__)


class PipelineState(TypedDict):
    """State passed between agents."""
    dataset_path: str
    file_type: str
    project_id: str
    config: Dict[str, Any]

    # Data Understanding
    data_profile: Dict[str, Any]
    target_column: str
    problem_type: str

    # Cleaning
    cleaned_data_path: str
    cleaning_report: Dict[str, Any]

    # EDA
    eda_report: Dict[str, Any]

    # Insights
    insights: Dict[str, Any]

    # ML
    ml_results: Dict[str, Any]
    model_path: str
    evaluation_report: Dict[str, Any]

    # Report
    final_report: Dict[str, Any]

    # Status
    current_step: str
    errors: list
    status: str


def create_analysis_pipeline() -> StateGraph:
    """Create the LangGraph analysis pipeline."""

    # Initialize agents
    data_agent = DataUnderstandingAgent()
    cleaning_agent = DataCleaningAgent()
    eda_agent = EDAAgent()
    insight_agent = InsightAgent()
    ml_agent = MLDecisionAgent()
    training_agent = ModelTrainingAgent()
    eval_agent = EvaluationAgent()
    report_agent = ReportAgent()

    # Define node functions
    def data_understanding_node(state: PipelineState) -> PipelineState:
        logger.info("🔍 Running Data Understanding Agent...")
        try:
            profile = data_agent.analyze(state["dataset_path"], state["file_type"])
            state["data_profile"] = profile
            state["target_column"] = profile.get("target_detection", {}).get("suggested_target", "")
            state["problem_type"] = profile.get("problem_type", {}).get("type", "regression")
            state["current_step"] = "data_understanding_complete"
        except Exception as e:
            state["errors"].append(f"Data Understanding: {str(e)}")
            state["status"] = "error"
        return state

    def data_cleaning_node(state: PipelineState) -> PipelineState:
        logger.info("🧹 Running Data Cleaning Agent...")
        try:
            cleaned_path, report = cleaning_agent.clean(
                state["dataset_path"], state["file_type"], state["config"]
            )
            state["cleaned_data_path"] = cleaned_path
            state["cleaning_report"] = report
            state["current_step"] = "cleaning_complete"
        except Exception as e:
            state["errors"].append(f"Data Cleaning: {str(e)}")
        return state

    def eda_node(state: PipelineState) -> PipelineState:
        logger.info("📊 Running EDA Agent...")
        try:
            eda_report = eda_agent.run_eda(
                state["cleaned_data_path"], state["target_column"]
            )
            state["eda_report"] = eda_report
            state["current_step"] = "eda_complete"
        except Exception as e:
            state["errors"].append(f"EDA: {str(e)}")
        return state

    def insight_node(state: PipelineState) -> PipelineState:
        logger.info("💡 Running Insight Generation Agent...")
        try:
            insights = insight_agent.generate_insights(
                state["data_profile"], state["eda_report"]
            )
            state["insights"] = insights
            state["current_step"] = "insights_complete"
        except Exception as e:
            state["errors"].append(f"Insights: {str(e)}")
        return state

    def ml_training_node(state: PipelineState) -> PipelineState:
        logger.info("🤖 Running ML Training Agent...")
        try:
            ml_results, model_path = training_agent.train(
                state["cleaned_data_path"],
                state["target_column"],
                state["problem_type"],
                state["config"],
            )
            state["ml_results"] = ml_results
            state["model_path"] = model_path
            state["current_step"] = "training_complete"
        except Exception as e:
            state["errors"].append(f"ML Training: {str(e)}")
        return state

    def evaluation_node(state: PipelineState) -> PipelineState:
        logger.info("📈 Running Evaluation Agent...")
        try:
            eval_report = eval_agent.evaluate(state["ml_results"], state["model_path"])
            state["evaluation_report"] = eval_report
            state["current_step"] = "evaluation_complete"
        except Exception as e:
            state["errors"].append(f"Evaluation: {str(e)}")
        return state

    def report_node(state: PipelineState) -> PipelineState:
        logger.info("📝 Running Report Generation Agent...")
        try:
            report = report_agent.generate(
                state["data_profile"],
                state["cleaning_report"],
                state["eda_report"],
                state["insights"],
                state["ml_results"],
                state["evaluation_report"],
                state["project_id"],
            )
            state["final_report"] = report
            state["current_step"] = "report_complete"
            state["status"] = "completed"
        except Exception as e:
            state["errors"].append(f"Report: {str(e)}")
        return state

    # Build graph
    workflow = StateGraph(PipelineState)

    # Add nodes
    workflow.add_node("data_understanding", data_understanding_node)
    workflow.add_node("data_cleaning", data_cleaning_node)
    workflow.add_node("eda", eda_node)
    workflow.add_node("insights", insight_node)
    workflow.add_node("ml_training", ml_training_node)
    workflow.add_node("evaluation", evaluation_node)
    workflow.add_node("report", report_node)

    # Define edges (sequential pipeline)
    workflow.set_entry_point("data_understanding")
    workflow.add_edge("data_understanding", "data_cleaning")
    workflow.add_edge("data_cleaning", "eda")
    workflow.add_edge("eda", "insights")
    workflow.add_edge("insights", "ml_training")
    workflow.add_edge("ml_training", "evaluation")
    workflow.add_edge("evaluation", "report")
    workflow.add_edge("report", END)

    return workflow.compile()


# Usage
def run_full_pipeline(
    dataset_path: str,
    file_type: str,
    project_id: str,
    config: Dict[str, Any] = None,
) -> PipelineState:
    """Execute the full analysis pipeline."""
    pipeline = create_analysis_pipeline()

    initial_state: PipelineState = {
        "dataset_path": dataset_path,
        "file_type": file_type,
        "project_id": project_id,
        "config": config or {},
        "data_profile": {},
        "target_column": "",
        "problem_type": "",
        "cleaned_data_path": "",
        "cleaning_report": {},
        "eda_report": {},
        "insights": {},
        "ml_results": {},
        "model_path": "",
        "evaluation_report": {},
        "final_report": {},
        "current_step": "started",
        "errors": [],
        "status": "running",
    }

    final_state = pipeline.invoke(initial_state)
    return final_state
