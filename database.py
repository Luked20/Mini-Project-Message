"""
Módulo de configuração e conexão com MongoDB.
Responsável por estabelecer conexão com o banco de dados e criar as coleções necessárias.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Classe responsável pelo gerenciamento da conexão com MongoDB."""
    
    def __init__(self):
        """Inicializa o gerenciador de banco de dados."""
        self.client = None
        self.db = None
        self.connection_string = ""
        self.database_name = "chat"
    
    def connect(self):
        """
        Estabelece conexão com o MongoDB e cria as coleções necessárias.
        
        Returns:
            bool: True se a conexão foi bem-sucedida, False caso contrário.
        """
        try:
            # Conecta ao MongoDB
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            
            # Testa a conexão
            self.client.admin.command('ping')
            
            # Seleciona o banco de dados
            self.db = self.client[self.database_name]
            
            # Cria as coleções e índices necessários
            self._create_collections()
            self._create_indexes()
            
            logger.info("Conexão com MongoDB estabelecida com sucesso!")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Erro ao conectar com MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao conectar com MongoDB: {e}")
            return False
    
    def _create_collections(self):
        """Cria as coleções necessárias no banco de dados."""
        try:
            # Cria coleção de usuários se não existir
            if "users" not in self.db.list_collection_names():
                self.db.create_collection("users")
                logger.info("Coleção 'users' criada com sucesso!")
            
            # Cria coleção de mensagens se não existir
            if "messages" not in self.db.list_collection_names():
                self.db.create_collection("messages")
                logger.info("Coleção 'messages' criada com sucesso!")
                
        except Exception as e:
            logger.error(f"Erro ao criar coleções: {e}")
    
    def _create_indexes(self):
        """Cria os índices necessários para otimizar as consultas."""
        try:
            # Índice único para username na coleção users
            self.db.users.create_index("username", unique=True)
            
            # Índices compostos para otimizar consultas de mensagens
            self.db.messages.create_index([("to_user", 1), ("status", 1)])
            self.db.messages.create_index("from_user")
            self.db.messages.create_index("sent_at")
            
            logger.info("Índices criados com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao criar índices: {e}")
    
    def get_database(self):
        """
        Retorna a instância do banco de dados.
        
        Returns:
            Database: Instância do banco de dados MongoDB.
        """
        return self.db
    
    def close_connection(self):
        """Fecha a conexão com o MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Conexão com MongoDB fechada.")
    
    def insert_mock_data(self):
        """
        Insere dados de mock (usuários de exemplo) se a coleção estiver vazia.
        """
        try:
            # Verifica se já existem usuários
            if self.db.users.count_documents({}) > 0:
                logger.info("Coleção 'users' já possui dados. Pulando inserção de mock.")
                return
            
            
            mock_users = [
                {"username": "@lucas", "created_at": datetime.utcnow()},
                {"username": "@igor", "created_at": datetime.utcnow()},
                {"username": "@pedro", "created_at": datetime.utcnow()},
                {"username": "@daniel", "created_at": datetime.utcnow()},
                {"username": "@jeh", "created_at": datetime.utcnow()}
            ]
            
            # Insere os usuários de mock
            result = self.db.users.insert_many(mock_users)
            logger.info(f"Dados de mock inseridos: {len(result.inserted_ids)} usuários criados.")
            
        except Exception as e:
            logger.error(f"Erro ao inserir dados de mock: {e}")

# Instância global do gerenciador de banco
db_manager = DatabaseManager()

