import json
import os
from typing import Dict, List
from models.product import Product

class JSONProductStore:
    """Classe para armazenar produtos em um arquivo JSON.
    
    Atributos: 
        file_path (str): Caminho para o arquivo JSON.
    """

    def __init__(self, file_path: str = 'products.json'):
        """
        Inicializa o armazenamento JSON.
        
        Args:
            file_path: Caminho para o arquivo JSON (padrão: products.json)
        """
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """
        Verifica se o arquivo existe, caso contrário cria um vazio.
        """
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)

    def _read_products(self) -> List[Dict]:
        """
        Lê todos os produtos do arquivo JSON.
        
        Returns:
            List[Dict]: Lista de produtos como dicionários
        """
        try:
            with open(self.file_path, 'r') as f:
                content = f.read().strip()
                # Se o arquivo estiver vazio, retorna uma lista vazia
                if not content:
                    return []
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            # Caso o arquivo não exista ou esteja malformado, retorna lista vazia
            return []

    def _write_products(self, products: List[Dict]):
        """
        Escreve produtos no arquivo JSON.
        
        Args:
            products: Lista de produtos como dicionários
        """
        with open(self.file_path, 'w') as f:
            json.dump(products, f, indent=2)

    def get_all(self) -> List[Product]:
        """
        Retorna todos os produtos.
        
        Returns:
            List[Product]: Lista de objetos Product
        """
        products_data = self._read_products()
        return [Product.from_dict(p) for p in products_data]
    
    def get_by_id(self, product_id: str) -> Product:
        """
        Obtém um produto pelo ID.
        
        Args:
            product_id: ID do produto a ser buscado
            
        Returns:
            Product: Objeto Product encontrado ou None se não existir
        """
        products_data = self._read_products()
        for p in products_data:
            if p['id'] == product_id:
                return Product.from_dict(p)
        return None
    
    def add(self, product: Product) -> None:
        """
        Adiciona um novo produto.
        
        Args:
            product: Objeto Product a ser adicionado
        """
        products_data = self._read_products()
        # Verifica se o produto já existe
        if any(p['id'] == product.id for p in products_data):
            raise ValueError(f"Produto com ID {product.id} já existe.")
        products_data.append(product.to_dict())
        self._write_products(products_data)

    def update(self, product: Product) -> bool:
        """
        Atualiza um produto existente.

        Args:
            product: Objeto Product com os dados atualizados

        Returns:
            bool: True se o produto foi atualizado, False se não foi encontrado
        """
        products_data = self._read_products()
        for i, p in enumerate(products_data):
            if p['id'] == product.id:
                products_data[i] = product.to_dict()
                self._write_products(products_data)
                return True
        return False
    
    def delete(self, product_id: str) -> bool:
        """Remove um produto pelo ID.
        
        Args:
            product_id: ID do produto a ser removido
            
        Returns:
            bool: True se o produto foi removido, False se não foi encontrado
        """
        products_data = self._read_products()
        new_products = [p for p in products_data if p['id'] != product_id]
        if len(new_products) != len(products_data):
            self._write_products(new_products)
            return True
        return False
