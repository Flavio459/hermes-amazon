import tempfile
import unittest
from pathlib import Path

from hermes_amazon.monitoring import (
    ChangeDetectionConfig,
    WatchRepository,
    build_changedetection_payload,
    create_watch_target,
    simulate_watch_event,
)
from hermes_amazon.products import ProductRepository, create_product


class MonitoringTests(unittest.TestCase):
    def test_create_watch_target_from_product(self) -> None:
        product = create_product(
            name="Monitor",
            category="eletronicos",
            affiliate_url="https://amazon.example/monitor",
        )
        target = create_watch_target(product, selector=".price")
        self.assertEqual(target.product_id, product.id)
        self.assertEqual(target.url, product.affiliate_url)
        self.assertEqual(target.selector, ".price")
        self.assertEqual(len(target.id), 12)

    def test_repository_add_from_product_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            product_repository = ProductRepository(Path(directory) / "products.json")
            watch_repository = WatchRepository(Path(directory) / "watch.json")
            product = product_repository.add(
                create_product(
                    name="Cadeira",
                    category="escritorio",
                    affiliate_url="https://amazon.example/cadeira",
                )
            )
            target = watch_repository.add_from_product(product.id, product_repository)
            self.assertEqual(watch_repository.get(target.id).product_id, product.id)
            self.assertEqual(len(watch_repository.list()), 1)

    def test_repository_rejects_missing_product(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            product_repository = ProductRepository(Path(directory) / "products.json")
            watch_repository = WatchRepository(Path(directory) / "watch.json")
            with self.assertRaises(KeyError):
                watch_repository.add_from_product("missing", product_repository)

    def test_repository_rejects_duplicate_watch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            product_repository = ProductRepository(Path(directory) / "products.json")
            watch_repository = WatchRepository(Path(directory) / "watch.json")
            product = product_repository.add(
                create_product(
                    name="Mouse",
                    category="eletronicos",
                    affiliate_url="https://amazon.example/mouse",
                )
            )
            watch_repository.add_from_product(product.id, product_repository)
            with self.assertRaises(ValueError):
                watch_repository.add_from_product(product.id, product_repository)

    def test_simulate_watch_event(self) -> None:
        product = create_product(
            name="Teclado",
            category="eletronicos",
            affiliate_url="https://amazon.example/teclado",
        )
        target = create_watch_target(product)
        event = simulate_watch_event(target, "price_drop", old_value="199.90", new_value="149.90", severity="notice")
        self.assertEqual(event.target_id, target.id)
        self.assertEqual(event.product_id, product.id)
        self.assertEqual(event.event_type, "price_drop")
        self.assertEqual(event.severity, "notice")

    def test_simulate_watch_event_rejects_unknown_type(self) -> None:
        product = create_product(
            name="Fone",
            category="eletronicos",
            affiliate_url="https://amazon.example/fone",
        )
        with self.assertRaises(ValueError):
            simulate_watch_event(create_watch_target(product), "unknown")

    def test_changedetection_payload_uses_product_and_target(self) -> None:
        product = create_product(
            name="Cadeira Premium",
            category="Home Office",
            affiliate_url="https://amazon.example/cadeira-premium",
            niche="Setup Trabalho",
        )
        target = create_watch_target(product, selector=".price")
        payload = build_changedetection_payload(product, target)
        self.assertEqual(payload.url, product.affiliate_url)
        self.assertEqual(payload.css_filter, ".price")
        self.assertEqual(payload.title, "Hermes Amazon - Cadeira Premium")
        self.assertEqual(payload.tag, "hermes-amazon,home-office,setup-trabalho")

    def test_changedetection_payload_rejects_mismatched_product(self) -> None:
        product = create_product(
            name="Produto A",
            category="teste",
            affiliate_url="https://amazon.example/a",
        )
        other = create_product(
            name="Produto B",
            category="teste",
            affiliate_url="https://amazon.example/b",
        )
        with self.assertRaises(ValueError):
            build_changedetection_payload(product, create_watch_target(other))

    def test_changedetection_config_requires_key(self) -> None:
        config = ChangeDetectionConfig(base_url="https://changedetection.example", api_key_present=False)
        self.assertIn("HERMES_CHANGEDETECTION_API_KEY ausente", config.validate())


if __name__ == "__main__":
    unittest.main()
