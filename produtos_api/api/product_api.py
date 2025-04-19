"""
Modulo principal da API de produtos.
"""

from http.server import BaseHTTPRequestHandler
from storage.json_storage import JSONProductStore
from .request_handler import RequestHandler
from models.product import Product
import uuid

class ProductAPI:
    """
    Classe que implementa a API REST para produtos.
    """

    def __init__(self, storage=None):
        """
        Inicializa a API com um sistema de armazenamento.
        
        Args:
            storage: Instancia de um sistema de armazenamento (padrao: JSONProductStorage)
            """
        self.storage = storage if storage is not None else JSONProductStore()

    def handle_request(self, request: BaseHTTPRequestHandler):
        """Manipula uma requisição HTTP e roteia para o método apropriado"""
        
        # Verificando o tipo da requisição
        if not isinstance(request, BaseHTTPRequestHandler):
            RequestHandler.send_error(request, 500, "Invalid request type")
            return
        
        try:
            path_info = RequestHandler.parse_path(request)
            path_parts = path_info['path_parts']

            # Roteamento básico
            if request.method == 'GET':  # Usar request.method para verificar método
                if len(path_parts) == 1 and path_parts[0] == 'products':
                    self._handle_get_all(request)
                elif len(path_parts) == 2 and path_parts[0] == 'products':
                    self._handle_get_one(request, path_parts[1])
                else:
                    RequestHandler.send_error(request, 404, "Endpoint not found")

            elif request.method == 'POST':
                if len(path_parts) == 1 and path_parts[0] == 'products':
                    self._handle_create(request)
                else:
                    RequestHandler.send_error(request, 404, "Endpoint not found")

            elif request.method == 'PUT':
                if len(path_parts) == 2 and path_parts[0] == 'products':
                    self._handle_update(request, path_parts[1])
                else:
                    RequestHandler.send_error(request, 404, "Endpoint not found")

            elif request.method == 'DELETE':
                if len(path_parts) == 2 and path_parts[0] == 'products':
                    self._handle_delete(request, path_parts[1])
                else:
                    RequestHandler.send_error(request, 404, "Endpoint not found")

            else:
                RequestHandler.send_error(request, 405, "Method not allowed")
        
        except ValueError as e:
            RequestHandler.send_error(request, 400, str(e))
        except Exception as e:
            RequestHandler.send_error(request, 500, "Internal server error")

    def _handle_get_all(self, request: BaseHTTPRequestHandler):
        """Manipula requisições GET para listar todos os produtos."""
        products = self.storage.get_all()
        products_data = [p.to_dict() for p in products]
        RequestHandler.send_response(request, 200, products_data)

    def _handle_get_one(self, request: BaseHTTPRequestHandler, product_id: str):
        """Manipula requisições GET para obter um produto específico."""
        product = self.storage.get_by_id(product_id)
        if product:
            RequestHandler.send_response(request, 200, product.to_dict())
        else:
            RequestHandler.send_error(request, 404, "Product not found")

    def _handle_create(self, request: BaseHTTPRequestHandler):
        """Manipula requisições POST para criar um novo produto."""
        data = RequestHandler.parse_json_body(request)

        # Validação básica
        if not data.get('name') or not data.get('price'):
            RequestHandler.send_error(request, 400, "Name and price are required")
            return
        
        try:
            price = float(data['price'])
        except ValueError:
            RequestHandler.send_error(request, 400, "Invalid price format")
            return
        
        # Cria novo produto
        product_id = str(uuid.uuid4())
        product = Product(
            id=product_id,
            name=data['name'],
            price=price,
            description=data.get('description')
        )

        self.storage.add(product)
        RequestHandler.send_response(request, 201, product.to_dict())

    def _handle_update(self, request: BaseHTTPRequestHandler, product_id: str):
        """Manipula requisições PUT para atualizar um produto existente."""
        product = self.storage.get_by_id(product_id)
        if not product:
            RequestHandler.send_error(request, 404, "Product not found")
            return

        data = RequestHandler.parse_json_body(request)

        # Atualiza campos permitidos
        name = data.get('name')
        price = data.get('price')
        description = data.get('description')

        if price is not None:
            try:
                price = float(price)
            except ValueError:
                RequestHandler.send_error(request, 400, "Invalid price format")
                return

        product.update(
            name=name,
            price=price,
            description=description
        )

        if self.storage.update(product):
            RequestHandler.send_response(request, 200, product.to_dict())
        else:
            RequestHandler.send_error(request, 500, "Failed to update product")

    def _handle_delete(self, request: BaseHTTPRequestHandler, product_id: str):
        """Manipula requisições DELETE para remover um produto."""
        if self.storage.delete(product_id):
            RequestHandler.send_response(request, 204)
        else:
            RequestHandler.send_error(request, 404, "Product not found")
