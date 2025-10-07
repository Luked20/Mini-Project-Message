
from pymongo.errors import DuplicateKeyError, OperationFailure
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRepository:
    """Repositório para operações com usuários."""
    
    def __init__(self, database):
        """
        Inicializa o repositório de usuários.
        
        Args:
            database: Instância do banco de dados MongoDB.
        """
        self.db = database
        self.collection = self.db.users
    
    def create_user(self, username: str) -> bool:
        """
        Cria um novo usuário no sistema.
        
        Args:
            username (str): Nome de usuário (com @).
            
        Returns:
            bool: True se o usuário foi criado com sucesso, False caso contrário.
        """
        try:
            user_doc = {
                "username": username,
                "created_at": datetime.utcnow()
            }
            
            result = self.collection.insert_one(user_doc)
            logger.info(f"Usuário {username} criado com sucesso. ID: {result.inserted_id}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"Usuário {username} já existe.")
            return False
        except Exception as e:
            logger.error(f"Erro ao criar usuário {username}: {e}")
            return False
    
    def find_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Busca um usuário pelo nome de usuário.
        
        Args:
            username (str): Nome de usuário a ser buscado.
            
        Returns:
            Optional[Dict]: Documento do usuário se encontrado, None caso contrário.
        """
        try:
            user = self.collection.find_one({"username": username})
            if user:
                logger.info(f"Usuário {username} encontrado.")
            else:
                logger.info(f"Usuário {username} não encontrado.")
            return user
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário {username}: {e}")
            return None
    
    def get_all_users(self, exclude_username: str = None) -> List[Dict]:
        """
        Retorna todos os usuários cadastrados.
        
        Args:
            exclude_username (str, optional): Username a ser excluído da lista.
            
        Returns:
            List[Dict]: Lista de usuários.
        """
        try:
            query = {}
            if exclude_username:
                query = {"username": {"$ne": exclude_username}}
            
            users = list(self.collection.find(query, {"username": 1, "created_at": 1}))
            logger.info(f"Encontrados {len(users)} usuários.")
            return users
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuários: {e}")
            return []
    
    def user_exists(self, username: str) -> bool:
        """
        Verifica se um usuário existe no sistema.
        
        Args:
            username (str): Nome de usuário a ser verificado.
            
        Returns:
            bool: True se o usuário existe, False caso contrário.
        """
        return self.find_user_by_username(username) is not None

class MessageRepository:
    """Repositório para operações com mensagens."""
    
    def __init__(self, database):
        """
        Inicializa o repositório de mensagens.
        
        Args:
            database: Instância do banco de dados MongoDB.
        """
        self.db = database
        self.collection = self.db.messages
    
    def create_message(self, from_user: str, to_user: str, encrypted_content: str) -> bool:
        """
        Cria uma nova mensagem no sistema.
        
        Args:
            from_user (str): Username do remetente.
            to_user (str): Username do destinatário.
            encrypted_content (str): Conteúdo criptografado da mensagem.
            
        Returns:
            bool: True se a mensagem foi criada com sucesso, False caso contrário.
        """
        try:
            message_doc = {
                "from_user": from_user,
                "to_user": to_user,
                "content_encrypted": encrypted_content,
                "status": "unread",
                "sent_at": datetime.utcnow()
            }
            
            result = self.collection.insert_one(message_doc)
            logger.info(f"Mensagem de {from_user} para {to_user} criada com sucesso. ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar mensagem: {e}")
            return False
    
    def get_unread_messages_by_user(self, username: str) -> List[Dict]:
        """
        Busca todas as mensagens não lidas de um usuário.
        
        Args:
            username (str): Username do destinatário.
            
        Returns:
            List[Dict]: Lista de mensagens não lidas.
        """
        try:
            query = {
                "to_user": username,
                "status": "unread"
            }
            
            messages = list(self.collection.find(query).sort("sent_at", -1))
            logger.info(f"Encontradas {len(messages)} mensagens não lidas para {username}.")
            return messages
            
        except Exception as e:
            logger.error(f"Erro ao buscar mensagens não lidas para {username}: {e}")
            return []
    
    def get_unread_messages_count(self, username: str) -> int:
        """
        Conta o número de mensagens não lidas de um usuário.
        
        Args:
            username (str): Username do destinatário.
            
        Returns:
            int: Número de mensagens não lidas.
        """
        try:
            query = {
                "to_user": username,
                "status": "unread"
            }
            
            count = self.collection.count_documents(query)
            logger.info(f"Usuário {username} possui {count} mensagens não lidas.")
            return count
            
        except Exception as e:
            logger.error(f"Erro ao contar mensagens não lidas para {username}: {e}")
            return 0
    
    def get_messages_by_sender(self, username: str, from_user: str) -> List[Dict]:
        """
        Busca mensagens de um remetente específico para um usuário.
        
        Args:
            username (str): Username do destinatário.
            from_user (str): Username do remetente.
            
        Returns:
            List[Dict]: Lista de mensagens do remetente.
        """
        try:
            query = {
                "to_user": username,
                "from_user": from_user,
                "status": "unread"
            }
            
            messages = list(self.collection.find(query).sort("sent_at", -1))
            logger.info(f"Encontradas {len(messages)} mensagens de {from_user} para {username}.")
            return messages
            
        except Exception as e:
            logger.error(f"Erro ao buscar mensagens de {from_user} para {username}: {e}")
            return []
    
    def mark_message_as_read(self, message_id: str) -> bool:
        """
        Marca uma mensagem como lida.
        
        Args:
            message_id (str): ID da mensagem a ser marcada como lida.
            
        Returns:
            bool: True se a mensagem foi marcada como lida, False caso contrário.
        """
        try:
            from bson import ObjectId
            
            result = self.collection.update_one(
                {"_id": ObjectId(message_id)},
                {"$set": {"status": "read"}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Mensagem {message_id} marcada como lida.")
                return True
            else:
                logger.warning(f"Mensagem {message_id} não encontrada ou já estava lida.")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao marcar mensagem {message_id} como lida: {e}")
            return False
    
    def get_message_by_id(self, message_id: str) -> Optional[Dict]:
        """
        Busca uma mensagem pelo ID.
        
        Args:
            message_id (str): ID da mensagem.
            
        Returns:
            Optional[Dict]: Documento da mensagem se encontrado, None caso contrário.
        """
        try:
            from bson import ObjectId
            
            message = self.collection.find_one({"_id": ObjectId(message_id)})
            if message:
                logger.info(f"Mensagem {message_id} encontrada.")
            else:
                logger.info(f"Mensagem {message_id} não encontrada.")
            return message
            
        except Exception as e:
            logger.error(f"Erro ao buscar mensagem {message_id}: {e}")
            return None

