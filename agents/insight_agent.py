# agents/insight_agent.py
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class BusinessInsights(BaseModel):
    business_domain: str = Field(description="Detected business domain")
    key_findings: List[str] = Field(description="Key data findings")
    recommendations: List[str] = Field(description="Business recommendations")
    trends: List[str] = Field(description="Identified trends")
    anomalies: List[str] = Field(description="Detected anomalies")
    executive_summary: str = Field(description="Executive summary paragraph")
    growth_opportunities: List[str] = Field(description="Growth opportunities")


class InsightAgent:
    """AI-powered business insight generation using LLM."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY,
        )
        self.parser = PydanticOutputParser(pydantic_object=BusinessInsights)

    def generate_insights(
        self,
        data_profile: Dict[str, Any],
        eda_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate business insights from data analysis."""

        # Prepare context for LLM
        context = self._prepare_context(data_profile, eda_report)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Data Analyst and Business Consultant.
Analyze the following dataset profile and EDA results to generate actionable business insights.
Provide specific, data-driven recommendations.
{format_instructions}"""),
            ("human", """Dataset Profile:
{profile}

EDA Results:
{eda}

Generate comprehensive business insights including:
1. Key findings from the data
2. Business recommendations
3. Identified trends
4. Anomalies or concerns
5. Growth opportunities
6. Executive summary"""),
        ])

        try:
            chain = prompt | self.llm | self.parser
            result = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "profile": json.dumps(data_profile, indent=2, default=str)[:3000],
                "eda": json.dumps(eda_report, indent=2, default=str)[:3000],
            })
            return result.model_dump()
        except Exception as e:
            logger.error(f"LLM insight generation failed: {e}")
            # Fallback: rule-based insights
            return self._rule_based_insights(data_profile, eda_report)

    def _prepare_context(self, profile: Dict, eda: Dict) -> str:
        """Prepare condensed context for LLM."""
        context_parts = []

        if "basic_info" in profile:
            info = profile["basic_info"]
            context_parts.append(f"Dataset: {info.get('rows', 0)} rows, {info.get('columns', 0)} columns")

        if "business_domain" in profile:
            context_parts.append(f"Domain: {profile['business_domain'].get('domain', 'unknown')}")

        if "problem_type" in profile:
            context_parts.append(f"ML Problem: {profile['problem_type'].get('type', 'unknown')}")

        if "quality_score" in profile:
            context_parts.append(f"Data Quality Score: {profile['quality_score']}/100")

        return "\n".join(context_parts)

    def _rule_based_insights(self, profile: Dict, eda: Dict) -> Dict[str, Any]:
        """Fallback rule-based insight generation."""
        insights = {
            "business_domain": profile.get("business_domain", {}).get("domain", "general"),
            "key_findings": [],
            "recommendations": [],
            "trends": [],
            "anomalies": [],
            "executive_summary": "",
            "growth_opportunities": [],
        }

        # Quality-based insights
        quality = profile.get("quality_score", 100)
        if quality < 70:
            insights["anomalies"].append(f"Data quality score is low ({quality}/100). Data governance improvements needed.")
            insights["recommendations"].append("Implement data validation rules at ingestion.")

        # Missing data insights
        missing = profile.get("missing_analysis", {})
        if missing.get("columns_with_missing", 0) > 0:
            insights["key_findings"].append(
                f"{missing['columns_with_missing']} columns have missing values."
            )

        # Correlation insights
        corr = eda.get("correlation_analysis", {})
        high_corr = corr.get("high_correlations", [])
        if high_corr:
            insights["key_findings"].append(
                f"Found {len(high_corr)} highly correlated feature pairs. Consider feature selection."
            )

        insights["executive_summary"] = (
            f"Analysis of {profile.get('basic_info', {}).get('rows', 'N/A')} records "
            f"across {profile.get('basic_info', {}).get('columns', 'N/A')} features "
            f"in the {insights['business_domain']} domain. "
            f"Data quality score: {quality}/100."
        )

        return insights
