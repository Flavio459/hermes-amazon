import unittest

from hermes_amazon.messaging import LocalMessagingAdapter, MessageEnvelope, MessageValidationError, validate_message_envelope


class MessagingTests(unittest.TestCase):
    def test_validate_serializable_envelope(self) -> None:
        envelope = MessageEnvelope(channel="hermes.local", payload={"ok": True})
        self.assertEqual(validate_message_envelope(envelope), [])

    def test_rejects_unserializable_payload(self) -> None:
        envelope = MessageEnvelope(channel="hermes.local", payload={"bad": set([1])})
        with self.assertRaises(MessageValidationError):
            validate_message_envelope(envelope)

    def test_local_adapter_stores_published_messages(self) -> None:
        adapter = LocalMessagingAdapter()
        receipt = adapter.publish({"kind": "boot", "status": "ok"})
        self.assertTrue(receipt.accepted)
        self.assertEqual(receipt.stored_messages, 1)
        self.assertEqual(len(adapter.messages), 1)


if __name__ == "__main__":
    unittest.main()
