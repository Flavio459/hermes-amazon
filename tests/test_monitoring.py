import tempfile
import unittest
from pathlib import Path

from hermes_amazon.monitoring import (
    WatchRepository,
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


if __name__ == "__main__":
    unittest.main()
