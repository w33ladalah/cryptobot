import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.analysis import AnalysisResult
from schema import AnalysisResultCreate
from repositories.analysis_result_repository import AnalysisResultRepository

class TestAnalysisResultRepository(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock(spec=Session)
        self.repo = AnalysisResultRepository(self.db)

    def test_create_analysis_result(self):
        analysis_result_data = AnalysisResultCreate(
            historical_data_key="hist_key",
            token_pairs_key="token_key",
            real_time_data_key="real_time_key",
            combined_data_key="combined_key",
            buying_decision="buy",
            trend="up",
            sentiment="positive",
            volatility="low",
            reasoning="reasoning",
            insights="insights"
        )
        token_pair_id = 1
        db_analysis_result = AnalysisResult(id=1, token_pair_id=token_pair_id, **analysis_result_data.__dict__)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = None

        with patch.object(self.db, 'query', return_value=MagicMock(filter=MagicMock(first=MagicMock(return_value=db_analysis_result)))):
            response = self.repo.create_analysis_result(token_pair_id, analysis_result_data)

        self.assertEqual(response.token_pair_id, token_pair_id)
        self.assertEqual(response.historical_data_key, "hist_key")

    def test_read_analysis_result(self):
        analysis_result_id = 1
        db_analysis_result = AnalysisResult(id=analysis_result_id)
        self.db.query.return_value.filter.return_value.first.return_value = db_analysis_result

        result = self.repo.read_analysis_result(analysis_result_id)
        self.assertEqual(result.id, analysis_result_id)

    def test_read_analysis_result_not_found(self):
        analysis_result_id = 1
        self.db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(HTTPException) as context:
            self.repo.read_analysis_result(analysis_result_id)
        self.assertEqual(context.exception.status_code, 404)

    def test_read_analysis_results(self):
        analysis_results = [AnalysisResult(id=1), AnalysisResult(id=2)]
        self.db.query.return_value.offset.return_value.limit.return_value.all.return_value = analysis_results

        results = self.repo.read_analysis_results(skip=0, limit=2)
        self.assertEqual(len(results), 2)

    def test_update_analysis_result(self):
        analysis_result_id = 1
        analysis_result_data = AnalysisResultCreate(
            historical_data_key="hist_key",
            token_pairs_key="token_key",
            real_time_data_key="real_time_key",
            combined_data_key="combined_key",
            buying_decision="buy",
            trend="up",
            sentiment="positive",
            volatility="low",
            reasoning="reasoning",
            insights="insights"
        )
        db_analysis_result = AnalysisResult(id=analysis_result_id)
        self.db.query.return_value.filter.return_value.first.return_value = db_analysis_result

        updated_result = self.repo.update_analysis_result(analysis_result_id, analysis_result_data)
        self.assertEqual(updated_result.historical_data_key, "hist_key")

    def test_delete_analysis_result(self):
        analysis_result_id = 1
        db_analysis_result = AnalysisResult(id=analysis_result_id)
        self.db.query.return_value.filter.return_value.first.return_value = db_analysis_result

        result = self.repo.delete_analysis_result(analysis_result_id)
        self.assertEqual(result.id, analysis_result_id)

    def test_delete_analysis_result_not_found(self):
        analysis_result_id = 1
        self.db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(HTTPException) as context:
            self.repo.delete_analysis_result(analysis_result_id)
        self.assertEqual(context.exception.status_code, 404)

if __name__ == '__main__':
    unittest.main()
