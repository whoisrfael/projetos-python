class Product:
    """
    Classe que representa um produto no sistema.
    
    Atributos(args):
        id (str): Identificador unico do produto
        name (str): Nome do produto
        price (float): Preço do produto
        description (str): Descrição detalhada do produto (opcional)
        create_at (str): Data de criação no formato ISO
        uptaded_at (str): Data de atualização no formato ISO
    """

    def __init__(self, id: str, name: str, price: float, description: str = None):
        """Inicializa um novo produto.
        
        Args:
            id: Identificador unico do produto
            name: Nome do produto
            price: Preço do produto
            description: Descrição detalhada (opcional)
        
        """

        self.id = id
        self.name = name
        self.price = price
        self.description = description
        self.created_at = self._current_datetime()
        self.updated_at = self.created_at

    def to_dict(self) -> dict:
        """
        Converte o objeto Product para um dicionário.
        
        Returns:
            dict: Representação do produto como dicionário
        """

        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,  # Corrigido aqui para passar o valor da variável
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def update(self, name: str = None, price: float = None, description: str = None):
        """
        Atualiza os campos do produto.
        
        Args: 
            name: Novo nome (opcional)
            price: Novo preço (opcional)
            description: Nova descrição (opcional)
        """

        if name is not None:
            self.name = name
        if price is not None:
            self.price = price
        if description is not None:
            self.description = description
        self.updated_at = self._current_datetime()

    @staticmethod
    def _current_datetime() -> str:
        """
        Retorna a data/hora atual no formato ISO.
        
        return:
            str: Data/hora no formato ISO 8601
        """

        from datetime import datetime
        return datetime.now().isoformat()
    
    @classmethod
    def from_dict(cls, data: dict):
        """Cria um objeto Product a partir de um dicionário
        
        Args: 
            data: dicionário com os dados do produto
            
        Returns:
            Product: Instância do produto"""
        
        product = cls(
            id=data['id'],
            name=data['name'],
            price=data['price'],
            description=data.get('description')
        )
        product.created_at = data['created_at']  # Corrigido aqui
        product.updated_at = data['updated_at']
        return product
