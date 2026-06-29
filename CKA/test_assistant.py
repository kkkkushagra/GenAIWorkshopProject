import unittest

from assistant import CollegeKnowledgeAssistant


class CollegeKnowledgeAssistantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assistant = CollegeKnowledgeAssistant("data")

    def test_classifies_academic_queries(self) -> None:
        self.assertEqual(self.assistant.classify_query("What are the grading rules?"), "Academic")

    def test_returns_source_citations_for_answers(self) -> None:
        answer = self.assistant.answer_query("What is the attendance requirement?")
        self.assertIn("attendance", answer.lower())
        self.assertIn("Attendance Policy", answer)

    def test_returns_substantive_content_not_title(self) -> None:
        answer = self.assistant.answer_query("What is the attendance requirement?")
        self.assertIn("75%", answer)
        self.assertNotIn("COLLEGE ATTENDANCE POLICY", answer)

    def test_uses_context_for_numeric_attendance_reasoning(self) -> None:
        answer = self.assistant.answer_query("My attendance is 66%. Can I appear in exams?")
        self.assertIn("66%", answer)
        self.assertIn("75%", answer)
        self.assertIn("Attendance Policy", answer)

    def test_uses_memory_for_follow_up_questions(self) -> None:
        self.assistant.answer_query("What is the attendance rule?")
        response = self.assistant.answer_query("What about the minimum percentage?")
        self.assertIn("75%", response)


if __name__ == "__main__":
    unittest.main()
