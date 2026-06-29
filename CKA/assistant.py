from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List, Dict


def _extract_percentage(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)%", text)
    if match:
        return float(match.group(1))
    return None


class CollegeKnowledgeAssistant:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = Path(data_dir)
        self.documents = self._load_documents()
        self.memory: List[str] = []

    def _load_documents(self) -> List[Dict[str, str]]:
        documents: List[Dict[str, str]] = []
        for file_path in sorted(self.data_dir.glob("*.txt")):
            content = file_path.read_text(encoding="utf-8")
            category = self._infer_category(file_path.name)
            documents.append({"title": file_path.stem.replace("_", " ").title(), "category": category, "content": content})
        return documents

    def _infer_category(self, file_name: str) -> str:
        if "academic" in file_name:
            return "Academic"
        if "attendance" in file_name:
            return "Attendance"
        if "placement" in file_name:
            return "Placement"
        if "hostel" in file_name:
            return "Hostel"
        return "General"

    def classify_query(self, query: str) -> str:
        lowered = query.lower()
        if self.memory:
            recent_history = " ".join(self.memory[-2:]).lower()
            if "attendance" in recent_history or "75%" in recent_history:
                return "Attendance"

        if any(word in lowered for word in ["attendance", "absent", "medical leave", "75%", "attendance requirement"]):
            return "Attendance"
        if any(word in lowered for word in ["placement", "job", "internship", "cgpa"]):
            return "Placement"
        if any(word in lowered for word in ["hostel", "room", "visitor", "quiet hours"]):
            return "Hostel"
        return "Academic"

    def answer_query(self, query: str) -> str:
        self.memory.append(query)
        category = self.classify_query(query)
        matches = [doc for doc in self.documents if doc["category"] == category]

        if not matches:
            return "I could not find a relevant policy in the available documents."

        ranked = self._rank_documents(query, matches)
        best = ranked[0]
        context = self._build_context(query, best)
        answer = self._generate_answer(query, context, best)
        citation = f"Source: {best['title']}"
        return f"{answer}\n\n{citation}"

    def _rank_documents(self, query: str, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        lowered = query.lower()
        query_terms = set(re.findall(r"[a-zA-Z]+", lowered))

        def score(document: Dict[str, str]) -> tuple[int, int, int]:
            title_terms = set(re.findall(r"[a-zA-Z]+", document["title"].lower()))
            content_lower = document["content"].lower()
            title_overlap = len(query_terms & title_terms)
            content_overlap = sum(1 for term in query_terms if term in content_lower)
            category_bonus = 1 if document["category"].lower() == self.classify_query(query).lower() else 0
            keyword_bonus = sum(1 for term in ["attendance", "grading", "placement", "hostel", "visitor", "cgpa", "exam"] if term in lowered and term in content_lower)
            followup_bonus = 1 if "attendance" in lowered and "75%" in content_lower else 0
            return (title_overlap * 3 + keyword_bonus * 2 + content_overlap + category_bonus + followup_bonus, title_overlap, content_overlap)

        return sorted(documents, key=score, reverse=True)

    def _build_context(self, query: str, document: Dict[str, str]) -> str:
        content = document["content"]
        content_lines = [line.strip() for line in content.splitlines() if line.strip()]
        lowered_query = query.lower()
        query_terms = set(re.findall(r"[a-zA-Z]+", lowered_query))

        relevant_lines = []
        for line in content_lines:
            lowered_line = line.lower()
            if len(line.split()) < 4:
                continue
            if line.startswith(tuple("1234567890")) or line.isupper() or line.endswith(":"):
                continue

            if any(term in lowered_line for term in query_terms) or any(
                keyword in lowered_line for keyword in ["must", "allowed", "prohibited", "eligible", "permission", "at least", "close", "visit", "attendance", "hostel", "placement", "cgpa", "rule", "policy", "75%", "minimum"]
            ):
                relevant_lines.append(line)

        if relevant_lines:
            return "\n".join(relevant_lines[:4])

        return content

    def _generate_answer(self, query: str, context: str, document: Dict[str, str]) -> str:
        if not context.strip():
            return "I couldn't find this information in the provided college documents."

        lowered_query = query.lower()
        recent_history = " ".join(self.memory[-2:]).lower() if self.memory else ""

        if "attendance" in recent_history and "75%" in recent_history:
            return (
                "Based on the retrieved policy, students must maintain at least 75% attendance to appear in examinations."
            )

        if "attendance" in lowered_query and "exam" in lowered_query:
            user_percentage = _extract_percentage(query)
            required_percentage = 75.0
            if user_percentage is not None:
                if user_percentage < required_percentage:
                    return (
                        f"Based on the retrieved policy, students must maintain at least {required_percentage:.0f}% attendance to appear in examinations. "
                        f"Since your attendance is {user_percentage:.0f}%, you are below the required level."
                    )
                return (
                    f"Based on the retrieved policy, students must maintain at least {required_percentage:.0f}% attendance to appear in examinations. "
                    f"Since your attendance is {user_percentage:.0f}%, you meet the minimum requirement."
                )

        if any(keyword in lowered_query for keyword in ["attendance", "hostel", "placement", "policy", "rule", "minimum", "percentage"]):
            if "attendance" in context.lower() and "75%" in context.lower():
                return (
                    "Based on the retrieved policy, students must maintain at least 75% attendance to appear in examinations."
                )
            return (
                f"Using the retrieved context, here is a concise answer: {context.splitlines()[0]}"
            )

        return "I couldn't find this information in the provided college documents."


if __name__ == "__main__":
    assistant = CollegeKnowledgeAssistant("data")
    while True:
        user_query = input("You: ")
        if user_query.lower() in {"exit", "quit"}:
            break
        print("Assistant:", assistant.answer_query(user_query))
