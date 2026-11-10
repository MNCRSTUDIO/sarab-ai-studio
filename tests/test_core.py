import unittest
from backend.api.server import _safe_filename
from backend.video_engine.editor import _safe_name, get_job
from backend.ai_engine.planner import create_video_plan
from backend.ai_engine.metadata import generate_seo_metadata

class CoreTests(unittest.TestCase):
    def test_safe_filename_removes_path(self):
        self.assertEqual(_safe_filename('../../hello world.jpg'), 'hello world.jpg')

    def test_output_name_is_mp4_and_safe(self):
        value = _safe_name('../../my video')
        self.assertTrue(value.endswith('.mp4'))
        self.assertNotIn('/', value)
        self.assertNotIn('..', value)

    def test_unknown_job_is_not_falsely_running(self):
        self.assertIsNone(get_job('definitely-not-a-real-job-id'))

    def test_planner_requires_prompt(self):
        with self.assertRaises(ValueError):
            create_video_plan('')

    def test_planner_is_explicitly_rule_based(self):
        plan = create_video_plan('School admission promotion', 'instagram', 20)
        self.assertEqual(plan['generated_by'], 'local rule-based planner (not generative AI)')
        self.assertEqual(plan['format'], '9:16 vertical')

    def test_metadata_has_required_fields(self):
        result = generate_seo_metadata('School annual day')
        self.assertTrue(result['title'])
        self.assertTrue(result['description'])
        self.assertTrue(result['hashtags'])

if __name__ == '__main__':
    unittest.main()
