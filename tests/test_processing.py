import unittest

from hermes_amazon.contracts import EventKind, HermesEvent, ModuleName
from hermes_amazon.messaging import LocalMessagingAdapter
from hermes_amazon.processing import LocalProcessingEngine, decide_route, validate_processing_event


class ProcessingTests(unittest.TestCase):
    def test_decide_route_for_sqs_message(self) -> None:
        event = HermesEvent(kind=EventKind.SQS_MESSAGE, source="queue-1", payload={"id": 1})
        decision = decide_route(event)
        self.assertEqual(decision.module, ModuleName.PROCESSING)
        self.assertEqual(decision.action, "consume_queue_message")

    def test_validate_processing_event_rejects_empty_source(self) -> None:
        event = HermesEvent(kind=EventKind.WEBHOOK_RECEIVED, source=" ", payload={})
        self.assertIn("source do evento nao pode ser vazio", validate_processing_event(event))

    def test_local_engine_can_emit_summary(self) -> None:
        engine = LocalProcessingEngine(messaging=LocalMessagingAdapter())
        event = HermesEvent(
            kind=EventKind.SNS_NOTIFICATION,
            source="sns-topic",
            payload={"message": "ok"},
            correlation_id="corr-1",
        )
        outcome = engine.run(event, emit=True)
        self.assertTrue(outcome.emitted)
        self.assertIsNotNone(outcome.receipt)
        self.assertEqual(outcome.decision.module, ModuleName.MESSAGING)


if __name__ == "__main__":
    unittest.main()
