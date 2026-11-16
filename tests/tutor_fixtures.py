"""Synthetic structured tutor fixtures, not native-verified teaching content."""
import json


def teaching(thai='สวัสดี', english='Hello', romanization='sà wàt dii', explanation=''):
  return dict(explanation=explanation, examples=[dict(thai=thai, english=english, romanization=romanization)],
              language_notes=[], reference_titles=[])


def tutorReply(**kwargs):
  return {'message': {'content': json.dumps(teaching(**kwargs), ensure_ascii=False)}}


def reviewedReply(*ids, explanation='Let’s practice this phrase.'):
  return {'message': {'content': json.dumps(dict(explanation=explanation, example_ids=list(ids),
                                                language_notes=[], reference_titles=[]), ensure_ascii=False)}}
