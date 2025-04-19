"""
Servidor HTTP principal para a API de produtos.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from api.product_api import ProductAPI  # Adicionando a importação da ProductAPI
from storage.json_storage import JSONProductStore
from models.product import Product


class ProductRequestHandler(BaseHTTPRequestHandler):
    """
    Manipulador de requisições HTTP para a API de produtos.
    """

    def __init__(self, *args, **kwargs):
        self.product_api = ProductAPI()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.product_api.handle_request(self)

    def do_POST(self):
        self.product_api.handle_request(self)

    def do_PUT(self):
        self.product_api.handle_request(self)

    def do_DELETE(self):
        self.product_api.handle_request(self)

def run_server(port: int = 8000):
    """
    Inicia o servidor HTTP.
    
    Args:
        port: Porta para o servidor escutar (padrão: 8000)
    """
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProductRequestHandler)

    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
