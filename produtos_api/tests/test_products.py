import unittest
from storage.json_storage import JSONProductStore
from models.product import Product

class TestJSONProductStore(unittest.TestCase):

    def setUp(self):
        """Configuração inicial para os testes."""
        self.store = JSONProductStore('test_products.json')
        self.test_product = Product(id='1', name='Test Product', price=100)

    def test_add_product(self):
        """Teste de adicionar um produto."""
        self.store.add(self.test_product)
        product = self.store.get_by_id('1')
        self.assertEqual(product.id, '1')
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, 100)

    def test_update_product(self):
        """Teste de atualização de um produto."""
        self.store.add(self.test_product)
        updated_product = Product(id='1', name='Updated Product', price=150)
        self.store.update(updated_product)
        product = self.store.get_by_id('1')
        self.assertEqual(product.name, 'Updated Product')
        self.assertEqual(product.price, 150)

    def test_delete_product(self):
        """Teste de remoção de um produto."""
        self.store.add(self.test_product)
        self.store.delete('1')
        product = self.store.get_by_id('1')
        self.assertIsNone(product)

    def test_get_all_products(self):
        """Teste para obter todos os produtos."""
        self.store.add(self.test_product)
        products = self.store.get_all()
        self.assertGreater(len(products), 0)

if __name__ == '__main__':
    unittest.main()
