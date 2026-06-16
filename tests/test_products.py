import tempfile
import unittest
from pathlib import Path

from hermes_amazon.products import ProductRepository, create_product, normalize_price


class ProductTests(unittest.TestCase):
    def test_create_product_normalizes_price_and_id(self) -> None:
        product = create_product(
            name="Cadeira Ergonomica",
            category="escritorio",
            affiliate_url="https://amazon.example/produto",
            price="129,90",
        )
        self.assertEqual(product.price, "129.90")
        self.assertEqual(len(product.id), 12)

    def test_create_product_rejects_invalid_link(self) -> None:
        with self.assertRaises(ValueError):
            create_product(name="Produto", category="teste", affiliate_url="amazon.example/produto")

    def test_repository_add_list_get_and_mark(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = ProductRepository(Path(directory) / "products.json")
            product = create_product(
                name="Mouse",
                category="eletronicos",
                affiliate_url="https://amazon.example/mouse",
                niche="home office",
            )
            repository.add(product)
            self.assertEqual(len(repository.list()), 1)
            self.assertEqual(repository.get(product.id).name, "Mouse")
            updated = repository.mark(product.id, "watching", notes="monitorar preco")
            self.assertEqual(updated.status, "watching")
            self.assertEqual(updated.notes, "monitorar preco")

    def test_repository_rejects_duplicate_product(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = ProductRepository(Path(directory) / "products.json")
            product = create_product(
                name="Teclado",
                category="eletronicos",
                affiliate_url="https://amazon.example/teclado",
            )
            repository.add(product)
            with self.assertRaises(ValueError):
                repository.add(product)

    def test_normalize_price_rejects_negative_values(self) -> None:
        with self.assertRaises(ValueError):
            normalize_price("-1")


if __name__ == "__main__":
    unittest.main()
