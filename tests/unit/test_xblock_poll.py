from __future__ import absolute_import
import unittest
import json

from xblock.field_data import DictFieldData
from mock import Mock

from poll.poll import PollBlock, SurveyBlock
from ..utils import MockRuntime, make_request


class TestPollBlock(unittest.TestCase):
    """
    Tests for XBlock Poll.
    """
    def setUp(self):
        """
        Test case setup
        """
        super(TestPollBlock, self).setUp()
        self.runtime = MockRuntime()
        self.poll_data = {
            'display_name': 'My Poll',
            'question': 'What is your favorite color?',
            'answers': [
                ['R', {'label': 'Red'}],
                ['B', {'label': 'Blue'}],
                ['G', {'label': 'Green'}],
                ['O', {'label': 'Other'}],
            ],
            'submissions_count': 5,
            'max_submissions': 1,
            'private_results': False,
            'feedback': 'My Feedback',
        }
        self.poll_block = PollBlock(
            self.runtime,
            DictFieldData(self.poll_data),
            None
        )

    def test_student_view_data(self):
        """
        Test the student_view_data results.
        """
        expected_poll_data = {
            'question': self.poll_data['question'],
            'answers': self.poll_data['answers'],
            'max_submissions': self.poll_data['max_submissions'],
            'private_results': self.poll_data['private_results'],
            'feedback': self.poll_data['feedback'],
        }

        student_view_data = self.poll_block.student_view_data()
        self.assertEqual(student_view_data, expected_poll_data)

    def test_student_view_user_state_handler(self):
        """
        Test the student_view_user_state handler results.
        """
        response = json.loads(
            self.poll_block.handle(
                'student_view_user_state',
                make_request('', method='GET')
            ).body.decode('utf-8')
        )
        expected_response = {
            u'choice': None,
            u'submissions_count': 5,
            u'tally': {'R': 0, 'B': 0, 'G': 0, 'O': 0},
        }
        self.assertEqual(response, expected_response)

    @classmethod
    def mock_user_states(cls):
        return (
            Mock(username='edx', state={'submissions_count': 1, 'choice': 'R'}),
            Mock(username='verified', state={'submissions_count': 1, 'choice': 'G'}),
            Mock(username='staff', state={'submissions_count': 1, 'choice': 'B'}),
            Mock(username='honor', state={'submissions_count': 1, 'choice': 'O'}),
            Mock(username='audit', state={'submissions_count': 1}),
            Mock(username='student', state={'submissions_count': 1, 'choice': None}),
        )

    def test_generate_report_data_dont_limit_responses(self):
        """
        Test generate_report_data iterator with no limit.
        """
        user_states = self.mock_user_states()
        report_data = self.poll_block.generate_report_data(user_states)
        report_data = list(report_data)
        self.assertEqual(len(report_data), 4)
        self.assertEqual(report_data[0],
                         ('edx', {'Question': self.poll_block.question,
                                  'Answer': 'Red',
                                  'Submissions count': 1}))
        self.assertNotIn('audit', [username for username, _ in report_data])
        self.assertNotIn('student', [username for username, _ in report_data])

    def test_generate_report_data_limit_responses(self):
        """
        Test generate_report_data iterator with limit.
        """
        user_states = self.mock_user_states()
        report_data = self.poll_block.generate_report_data(user_states, limit_responses=2)
        report_data = list(report_data)
        self.assertEqual(len(report_data), 2)
        self.assertEqual(report_data[0],
                         ('edx', {'Question': self.poll_block.question,
                                  'Answer': 'Red',
                                  'Submissions count': 1}))

        report_data = self.poll_block.generate_report_data(user_states, limit_responses=0)
        report_data = list(report_data)
        self.assertEqual(len(report_data), 0)

    def test_indexing(self):
        self.assertEqual(
            self.poll_block.index_dictionary(),
            {
                'content': {
                    'display_name': 'My Poll',
                    'question': 'What is your favorite color?',
                    'option_0': 'Red',
                    'option_1': 'Blue',
                    'option_2': 'Green',
                    'option_3': 'Other',
                },
                'content_type': 'Poll'
            }
        )
class TestSurveyBlock(unittest.TestCase):
    """
    Tests for XBlock Survey.
    """
    def setUp(self):
        """
        Test case setup
        """
        super(TestSurveyBlock, self).setUp()
        self.runtime = MockRuntime()
        self.survery_data = {
            'display_name': 'My Survey',
            'questions': [
                ['enjoy', {'label': 'Are you enjoying the course?'}],
                ['recommend', {'label': 'Would you recommend this course to your friends?'}],
                ['learn', {'label': 'Do you think you will learn a lot?'}]
            ],
            'answers': [
                ['Y', 'Yes'],
                ['N', 'No'],
                ['M', 'Maybe']
            ],
            'submissions_count': 5,
            'max_submissions': 1,
            'private_results': False,
            'feedback': 'My Feedback',
            'block_name': 'My Block Name',
        }
        self.survey_block = SurveyBlock(
            self.runtime,
            DictFieldData(self.survery_data),
            None
        )

    def test_student_view_data(self):
        """
        Test the student_view_data results.
        """
        expected_survery_data = {
            'questions': self.survery_data['questions'],
            'answers': self.survery_data['answers'],
            'max_submissions': self.survery_data['max_submissions'],
            'private_results': self.survery_data['private_results'],
            'feedback': self.survery_data['feedback'],
            'block_name': self.survery_data['block_name'],
        }

        student_view_data = self.survey_block.student_view_data()
        self.assertEqual(student_view_data, expected_survery_data)

    def test_student_view_user_state_handler(self):
        """
        Test the student_view_user_state handler results.
        """
        response = json.loads(
            self.survey_block.handle(
                'student_view_user_state',
                make_request('', method='GET')
            ).body.decode('utf-8')
        )
        expected_response = {
            u'choices': None,
            u'submissions_count': 5,
            u'tally': {
                u'enjoy': {u'M': 0, u'N': 0, u'Y': 0},
                u'learn': {u'M': 0, u'N': 0, u'Y': 0},
                u'recommend': {u'M': 0, u'N': 0, u'Y': 0},
            },
        }
        self.assertEqual(response, expected_response)

    @classmethod
    def mock_user_states(cls):
        return (
            Mock(
                username='edx',
                state={
                    'submissions_count': 1,
                    'choices': {'enjoy': 'Y', 'recommend': 'N', 'learn': 'M'}
                }
            ),
            Mock(
                username='verified',
                state={
                    'submissions_count': 1,
                    'choices': {'enjoy': 'M', 'recommend': 'N', 'learn': 'Y'}
                }
            ),
            Mock(
                username='staff',
                state={
                    'submissions_count': 1,
                    'choices': {'enjoy': 'N', 'recommend': 'N', 'learn': 'N'}
                }
            ),
            Mock(
                username='honor',
                state={
                    'submissions_count': 1,
                    'choices': {'enjoy': 'Y', 'recommend': 'N', 'learn': 'M'}
                }
            ),
            Mock(
                username='audit',
                state={
                    'submissions_count': 1,
                }
            ),
            Mock(
                username='student',
                state={
                    'submissions_count': 1,
                    'choices': None,
                }
            ),
        )

    def test_generate_report_data_dont_limit_responses(self):
        """
        Test generate_report_data iterator with no limit.
        """
        user_states = self.mock_user_states()
        report_data = self.survey_block.generate_report_data(user_states)
        report_data = list(report_data)
        self.assertEqual(len(report_data), 12)
        # each choice of a user gets its own row
        # so the first three rows should be edx's choices
        self.assertEqual(['edx', 'edx', 'edx', 'verified'],
                         [username for username, _ in report_data[:4]])
        self.assertEqual(
            set(['Yes', 'No', 'Maybe']),
            set([data['Answer'] for _, data in report_data[:4]])
        )
        self.assertNotIn('audit', [username for username, _ in report_data])
        self.assertNotIn('student', [username for username, _ in report_data])

    def test_generate_report_data_limit_responses(self):
        """
        Test generate_report_data iterator with limit.
        """
        user_states = self.mock_user_states()
        report_data = self.survey_block.generate_report_data(user_states, limit_responses=2)
        report_data = list(report_data)
        self.assertEqual(len(report_data), 2)
        # each choice of a user gets its own row
        # so the first two rows should be edx's choices
        self.assertEqual(['edx', 'edx'],
                         [username for username, _ in report_data])
        self.assertTrue(
            set([data['Answer'] for _, data in report_data[:3]]) <= set(['Yes', 'No', 'Maybe'])
        )

        report_data = self.survey_block.generate_report_data(user_states, limit_responses=0)
        report_data = list(report_data)
        self.assertEqual(len(report_data), 0)

    def test_indexing(self):
        self.assertEqual(
            self.survey_block.index_dictionary(),
            {
                'content': {
                    'display_name': 'My Survey',
                    'question_0': 'Are you enjoying the course?',
                    'question_1': 'Would you recommend this course to your friends?',
                    'question_2': 'Do you think you will learn a lot?',
                    'option_0': 'Yes',
                    'option_1': 'No',
                    'option_2': 'Maybe',
                },
                'content_type': 'Survey'
            }
        )


class TestSurveyTextQuestions(unittest.TestCase):
    """
    Tests for short-answer and long-answer (free text) survey questions.
    """
    def setUp(self):
        super(TestSurveyTextQuestions, self).setUp()
        self.runtime = MockRuntime()
        self.runtime.publish = Mock()
        self.data = {
            'display_name': 'Mixed Survey',
            'questions': [
                ['enjoy', {'label': 'Are you enjoying the course?', 'img': None, 'img_alt': None}],
                ['name', {'label': 'Your job title', 'img': None, 'img_alt': None, 'type': 'short_text'}],
                ['comments', {'label': 'Any comments?', 'img': None, 'img_alt': None, 'type': 'long_text'}],
            ],
            'answers': [['Y', 'Yes'], ['N', 'No']],
            'max_submissions': 0,
            'private_results': True,
        }
        self.block = SurveyBlock(self.runtime, DictFieldData(self.data), None)

    def vote(self, choices, block=None):
        block = block or self.block
        return json.loads(block.handle('vote', make_request(json.dumps(choices))).body.decode('utf-8'))

    def submitted_event(self):
        events = [call[0][2] for call in self.runtime.publish.call_args_list if call[0][1] == 'xblock.survey.submitted']
        return events[-1]

    def test_vote_with_text_answers(self):
        result = self.vote({'enjoy': 'Y', 'name': '  مهندس  ', 'comments': 'تجربة رائعة\nشكرًا'})
        self.assertTrue(result['success'], result['errors'])
        self.assertEqual(self.block.choices, {'enjoy': 'Y', 'name': 'مهندس', 'comments': 'تجربة رائعة\nشكرًا'})
        self.assertEqual(self.block.tally, {'enjoy': {'Y': 1, 'N': 0}})

    def test_text_answers_stay_out_of_tracking_event(self):
        self.vote({'enjoy': 'N', 'name': 'secret', 'comments': ''})
        event = self.submitted_event()
        self.assertEqual(event['choices'], {'enjoy': 'N'})
        self.assertEqual(event['answered_text_questions'], ['name'])
        self.assertNotIn('secret', json.dumps(event))

    def test_blank_text_answers_are_accepted(self):
        result = self.vote({'enjoy': 'Y', 'name': '', 'comments': '   '})
        self.assertTrue(result['success'], result['errors'])
        self.assertEqual(self.block.choices['comments'], '')

    def test_text_answer_length_caps(self):
        self.assertFalse(self.vote({'enjoy': 'Y', 'name': 'x' * 256, 'comments': ''})['success'])
        self.assertFalse(self.vote({'enjoy': 'Y', 'name': '', 'comments': 'x' * 5001})['success'])
        self.assertTrue(self.vote({'enjoy': 'Y', 'name': 'x' * 255, 'comments': 'x' * 5000})['success'])

    def test_text_answer_must_be_a_string(self):
        result = self.vote({'enjoy': 'Y', 'name': ['a'], 'comments': ''})
        self.assertFalse(result['success'])
        self.assertIsNone(self.block.choices)

    def test_choice_question_still_needs_a_known_answer(self):
        self.assertFalse(self.vote({'enjoy': 'free text', 'name': '', 'comments': ''})['success'])

    def test_all_questions_must_be_sent(self):
        self.assertFalse(self.vote({'enjoy': 'Y', 'name': 'x'})['success'])

    def test_text_vote_is_kept_by_get_choices(self):
        self.vote({'enjoy': 'Y', 'name': 'not an answer key', 'comments': 'also not'})
        self.assertEqual(self.block.get_choices()['name'], 'not an answer key')

    def test_revote_after_choice_question_becomes_text(self):
        self.vote({'enjoy': 'Y', 'name': 'a', 'comments': 'b'})
        self.block.questions = [
            ['enjoy', {'label': 'Are you enjoying the course?', 'img': None, 'img_alt': None, 'type': 'long_text'}],
            ['name', {'label': 'Your job title', 'img': None, 'img_alt': None, 'type': 'short_text'}],
            ['comments', {'label': 'Any comments?', 'img': None, 'img_alt': None, 'type': 'long_text'}],
        ]
        result = self.vote({'enjoy': 'now text', 'name': 'a', 'comments': 'b'})
        self.assertTrue(result['success'], result['errors'])
        self.assertEqual(self.block.tally, {})

    def test_revote_after_text_question_becomes_choice(self):
        self.vote({'enjoy': 'Y', 'name': 'a', 'comments': 'b'})
        self.block.questions = [
            ['enjoy', {'label': 'Are you enjoying the course?', 'img': None, 'img_alt': None}],
            ['name', {'label': 'Your job title', 'img': None, 'img_alt': None}],
            ['comments', {'label': 'Any comments?', 'img': None, 'img_alt': None, 'type': 'long_text'}],
        ]
        # The stored text is no longer a valid answer: the vote is dropped, as when answers change.
        self.assertIsNone(self.block.get_choices())
        result = self.vote({'enjoy': 'N', 'name': 'Y', 'comments': ''})
        self.assertTrue(result['success'], result['errors'])
        self.assertEqual(self.block.tally, {'enjoy': {'Y': 0, 'N': 1}, 'name': {'Y': 1, 'N': 0}})

    def test_tally_detail_lists_choice_questions_only(self):
        self.vote({'enjoy': 'Y', 'name': 'a', 'comments': 'b'})
        tally, total = self.block.tally_detail()
        self.assertEqual([question['key'] for question in tally], ['enjoy'])
        self.assertEqual(total, 1)

    def test_renderable_answers_carry_type_and_saved_text(self):
        self.vote({'enjoy': 'Y', 'name': 'مهندس', 'comments': ''})
        rendered = dict(self.block.renderable_answers(self.block.questions, self.block.choices))
        self.assertEqual(rendered['enjoy']['type'], 'choice')
        self.assertIsNone(rendered['enjoy']['max_length'])
        self.assertEqual(rendered['name']['type'], 'short_text')
        self.assertEqual(rendered['name']['max_length'], 255)
        self.assertEqual(rendered['name']['choice'], 'مهندس')
        self.assertEqual(rendered['comments']['max_length'], 5000)

    def test_generate_report_data_returns_text(self):
        states = [Mock(username='learner', state={
            'submissions_count': 1, 'choices': {'enjoy': 'Y', 'name': 'مهندس', 'comments': ''}})]
        report = dict((row['Question'], row['Answer']) for _, row in self.block.generate_report_data(states))
        self.assertEqual(report, {
            'Are you enjoying the course?': 'Yes', 'Your job title': 'مهندس', 'Any comments?': ''})

    def test_prepare_data_returns_text_and_tolerates_missing_answers(self):
        student = Mock(id=7, username='learner', email='learner@example.com')
        rows = [
            Mock(student=student, state=json.dumps({'choices': {'enjoy': 'N', 'name': 'مهندس', 'comments': 'نص'}})),
            Mock(student=Mock(id=8, username='old', email='old@example.com'),
                 state=json.dumps({'choices': {'enjoy': 'Y'}})),
        ]
        self.block.student_module_queryset = Mock(return_value=rows)
        data = self.block.prepare_data()
        # Questions are sorted by key: comments, enjoy, name.
        self.assertEqual(data[0], ['user_id', 'username', 'user_email', 'Any comments?',
                                   'Are you enjoying the course?', 'Your job title'])
        self.assertEqual(data[1], [7, 'learner', 'learner@example.com', 'نص', 'No', 'مهندس'])
        self.assertEqual(data[2], [8, 'old', 'old@example.com', '', 'Yes', ''])

    def studio_payload(self, question_type):
        return {
            'display_name': 'Survey',
            'answers': [{'key': 'Y', 'label': 'Yes'}],
            'questions': [{'key': 'q1', 'label': 'Question one', 'img': '', 'img_alt': '', 'type': question_type}],
            'max_submissions': 1,
            'private_results': True,
            'feedback': '',
        }

    def studio_submit(self, payload):
        return json.loads(self.block.handle('studio_submit', make_request(json.dumps(payload))).body.decode('utf-8'))

    def test_studio_submit_stores_text_type(self):
        self.assertTrue(self.studio_submit(self.studio_payload('long_text'))['success'])
        self.assertEqual(self.block.questions[0][1]['type'], 'long_text')

    def test_studio_submit_keeps_choice_questions_unchanged(self):
        self.assertTrue(self.studio_submit(self.studio_payload('choice'))['success'])
        self.assertNotIn('type', self.block.questions[0][1])

    def test_studio_submit_rejects_unknown_type(self):
        result = self.studio_submit(self.studio_payload('essay'))
        self.assertFalse(result['success'])

    def test_load_questions_returns_type(self):
        items = json.loads(self.block.handle('load_questions', make_request('{}')).body.decode('utf-8'))['items']
        self.assertEqual([item['type'] for item in items], ['choice', 'short_text', 'long_text'])

    def test_questions_with_type_survive_olx_serialisation(self):
        field = SurveyBlock.fields['questions']
        self.assertEqual(field.from_string(field.to_string(self.data['questions'])), self.data['questions'])


class TestLegacySurveyUnchanged(unittest.TestCase):
    """
    A survey saved before question types existed behaves exactly as before.
    """
    def test_legacy_vote_and_event(self):
        runtime = MockRuntime()
        runtime.publish = Mock()
        block = SurveyBlock(runtime, DictFieldData({
            'questions': [['enjoy', {'label': 'Enjoy?', 'img': None, 'img_alt': None}]],
            'answers': [['Y', 'Yes'], ['N', 'No']],
        }), None)
        result = json.loads(block.handle('vote', make_request(json.dumps({'enjoy': 'Y'}))).body.decode('utf-8'))
        self.assertTrue(result['success'], result['errors'])
        self.assertEqual(block.tally, {'enjoy': {'Y': 1, 'N': 0}})
        event = [call[0][2] for call in runtime.publish.call_args_list if call[0][1] == 'xblock.survey.submitted'][-1]
        self.assertEqual(event['choices'], {'enjoy': 'Y'})
        self.assertEqual(event['answered_text_questions'], [])
