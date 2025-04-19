"""
Modulo para manipulaçao de requisiçoes HTTP basicas.

"""

from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

class RequestHandler:
    """
    Classe auxiliar para processar requisiçoes HTTP.
    """

    @staticmethod
    def parse_path(request: BaseHTTPRequestHandler) -> dict:
        """
        Analisa o caminho da URL e extrai parametros.
        
        Args: 
            request: Objeto de requisições HTTP
            
        Returns:
            dict: Dicionario com componentes do caminho e parametros de consulta
        """
        parsed = urlparse(request.path)
        path_parts = [p for p in parsed.path.split('/')if p]
        query_params = parse_qs(parsed.query)

        return {
            'path_parts': path_parts,
            'query_params': query_params,
            'path': parsed.path
        }
    
    @staticmethod
    def parse_json_body(request: BaseHTTPRequestHandler) -> dict:
        """
        Analisa o corpo da requisição como JSON.
        
        Args:
            request: Objeto de requisição HTTP
            
        Returns:
            dict: Dicionario com os dados do corpo
            
        Raises: 
            ValueError: Se o corpo nao for um JSON valido
        """


        content_length = int(request.headers.get('Contetn-Length', 0))
        if content_length == 0:
            return {}
        
        body = request.rfile.read(content_length).decode('utf-8')
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON")
        
    
    @staticmethod
    def send_response(request: BaseHTTPRequestHandler, status_code: int, data: dict = None):
        """
        Envia uma resposta HTTP com JSON.
        
        Args:
            request: Objeto de requisição HTTP
            status_code: Codigo de status HTTP
            data: Dados a serem enviados como JSON (opcional)
            """
        request.send_response(status_code)
        request.send_header('Content-type', 'application/json')
        request.end_headers()

        if data is not None:
            request.wfile.write(json.dumps(data).encode('utf-8'))

    @staticmethod
    def send_error(request: BaseHTTPRequestHandler, status_code: int, message: str):
        """
        Envia uma resposta de erro HTTP.
        
        Args:
            request: Objeto de requisiçao HTTP
            status_code: Codigo de status HTTP
            message: Mensagem de erro"""

        RequestHandler.send_response(request,status_code, {'erro': message})        