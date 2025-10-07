"""
Módulo de serviços (Lógica de Negócio).
Orquestra as operações do sistema e contém a lógica de negócio.
"""

from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime

from database import db_manager
from repository import UserRepository, MessageRepository
from crypto import crypto_manager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserService:
    """Serviço para operações relacionadas a usuários."""
    
    def __init__(self):
        """Inicializa o serviço de usuários."""
        self.user_repo = None
    
    def _ensure_repo(self):
        """Garante que o repositório está inicializado."""
        if self.user_repo is None:
            self.user_repo = UserRepository(db_manager.get_database())
    
    def authenticate_user(self, username: str) -> bool:
   
        try:
            # Garante que o repositório de usuários está inicializado
            self._ensure_repo()
            
            # Valida formato do username - deve começar com @
            if not username.startswith('@'):
                logger.warning(f"Username {username} nao possui formato valido (deve comecar com @)")
                return False  # Retorna False se formato inválido
            
            # Verifica se o usuário existe no banco de dados
            user_exists = self.user_repo.user_exists(username)
            
            # Verifica resultado da consulta
            if user_exists:
                # Usuário encontrado - autenticação bem-sucedida
                logger.info(f"Usuario {username} autenticado com sucesso.")
                return True
            else:
                # Usuário não encontrado - autenticação falhou
                logger.warning(f"Usuario {username} nao encontrado.")
                return False
                
        except Exception as e:
            # Trata erros durante o processo de autenticação
            logger.error(f"Erro ao autenticar usuario {username}: {e}")
            return False  # Retorna False em caso de erro
    
    def get_available_users(self, current_user: str) -> List[Dict]:
     
        try:
            # Garante que o repositório de usuários está inicializado
            self._ensure_repo()
            
            # Busca todos os usuários excluindo o usuário atual
            users = self.user_repo.get_all_users(exclude_username=current_user)
            
            # Registra resultado da busca no log
            logger.info(f"Retornados {len(users)} usuarios disponiveis para {current_user}")
            
            # Retorna lista de usuários disponíveis
            return users
            
        except Exception as e:
            # Trata erros durante a busca de usuários
            logger.error(f"Erro ao buscar usuarios disponiveis: {e}")
            return []  # Retorna lista vazia em caso de erro
    
    def validate_recipient(self, recipient: str) -> bool:
  
        try:
            # Garante que o repositório de usuários está inicializado
            self._ensure_repo()
            
            # Valida formato do username - deve começar com @
            if not recipient.startswith('@'):
                return False  # Retorna False se formato inválido
            
            # Verifica se o destinatário existe no banco de dados
            return self.user_repo.user_exists(recipient)
            
        except Exception as e:
            # Trata erros durante a validação
            logger.error(f"Erro ao validar destinatario {recipient}: {e}")
            return False  # Retorna False em caso de erro

class MessageService:
    """Serviço para operações relacionadas a mensagens."""
    
    def __init__(self):
        """Inicializa o serviço de mensagens."""
        self.message_repo = None
        self.user_service = UserService()
    
    def _ensure_repo(self):
        """Garante que o repositório está inicializado."""
        if self.message_repo is None:
            self.message_repo = MessageRepository(db_manager.get_database())
    
    def send_message(self, from_user: str, to_user: str, message: str, secret_key: str) -> Tuple[bool, str]:
       
   
        try:
            # Garante que o repositório de mensagens está inicializado
            self._ensure_repo()
            
            # Validação 1: Verifica tamanho mínimo da mensagem
            if len(message) < 50:
                return False, "A mensagem deve ter pelo menos 50 caracteres."
            
            # Validação 2: Verifica se o destinatário existe no sistema
            if not self.user_service.validate_recipient(to_user):
                return False, f"Destinatario {to_user} nao encontrado."
            
            # Validação 3: Verifica força da chave secreta
            if not crypto_manager.validate_password_strength(secret_key):
                return False, "A chave secreta deve ter pelo menos 8 caracteres, contendo letras e numeros."
            
            # Processo de criptografia da mensagem
            try:
                # Criptografa a mensagem usando AES-256-GCM
                encrypted_content = crypto_manager.encrypt_message(message, secret_key)
            except Exception as e:
                # Retorna erro se criptografia falhar
                return False, f"Erro na criptografia: {str(e)}"
            
            # Salva a mensagem criptografada no banco de dados
            success = self.message_repo.create_message(from_user, to_user, encrypted_content)
            
            # Verifica resultado da operação de salvamento
            if success:
                # Mensagem salva com sucesso
                logger.info(f"Mensagem enviada de {from_user} para {to_user}")
                return True, "Mensagem enviada com sucesso!"
            else:
                # Falha ao salvar mensagem
                return False, "Erro ao salvar mensagem no banco de dados."
                
        except Exception as e:
            # Trata erros gerais durante o envio
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False, f"Erro interno: {str(e)}"
    
    def get_unread_messages_count(self, username: str) -> int:
    
        try:
            # Garante que o repositório de mensagens está inicializado
            self._ensure_repo()
            
            # Busca contagem de mensagens não lidas do usuário
            return self.message_repo.get_unread_messages_count(username)
            
        except Exception as e:
            # Trata erros durante a contagem
            logger.error(f"Erro ao contar mensagens nao lidas: {e}")
            return 0  # Retorna 0 em caso de erro
    
    def get_unread_messages_grouped(self, username: str) -> Dict[str, List[Dict]]:
       
        try:
            # Garante que o repositório de mensagens está inicializado
            self._ensure_repo()
            
            # Busca todas as mensagens não lidas do usuário
            messages = self.message_repo.get_unread_messages_by_user(username)
            
            # Agrupa mensagens por remetente
            grouped_messages = {}
            for message in messages:
                # Obtém username do remetente
                sender = message['from_user']
                
                # Cria lista para o remetente se não existir
                if sender not in grouped_messages:
                    grouped_messages[sender] = []
                
                # Adiciona mensagem à lista do remetente
                grouped_messages[sender].append(message)
            
            # Registra resultado no log
            logger.info(f"Retornadas mensagens de {len(grouped_messages)} remetentes para {username}")
            
            # Retorna mensagens agrupadas
            return grouped_messages
            
        except Exception as e:
            # Trata erros durante o agrupamento
            logger.error(f"Erro ao buscar mensagens agrupadas: {e}")
            return {}  # Retorna dicionário vazio em caso de erro
    
    def read_message(self, message_id: str, secret_key: str, username: str) -> Tuple[bool, str, str]:
   
        try:
            # Garante que o repositório de mensagens está inicializado
            self._ensure_repo()
            
            # Busca a mensagem pelo ID no banco de dados
            message = self.message_repo.get_message_by_id(message_id)
            
            # Verifica se a mensagem foi encontrada
            if not message:
                return False, "Mensagem nao encontrada.", ""
            
            # Validação 1: Verifica se a mensagem pertence ao usuário
            if message['to_user'] != username:
                return False, "Acesso negado. Esta mensagem nao e sua.", ""
            
            # Validação 2: Verifica se a mensagem já foi lida
            if message['status'] == 'read':
                return False, "Esta mensagem ja foi lida.", ""
            
            # Processo de descriptografia da mensagem
            try:
                # Tenta descriptografar usando a chave secreta fornecida
                decrypted_content = crypto_manager.decrypt_message(
                    message['content_encrypted'], 
                    secret_key
                )
                
                # Marca mensagem como lida no banco de dados
                self.message_repo.mark_message_as_read(message_id)
                
                # Registra sucesso no log
                logger.info(f"Mensagem {message_id} lida com sucesso por {username}")
                
                # Retorna sucesso com conteúdo descriptografado
                return True, "Mensagem lida com sucesso!", decrypted_content
                
            except Exception as e:
                # Falha na descriptografia - chave incorreta
                logger.warning(f"Falha na descriptografia da mensagem {message_id}: {e}")
                return False, "Chave incorreta! Acesso negado.", ""
                
        except Exception as e:
            # Trata erros gerais durante a leitura
            logger.error(f"Erro ao ler mensagem {message_id}: {e}")
            return False, f"Erro interno: {str(e)}", ""
    
    def get_messages_from_sender(self, username: str, sender: str) -> List[Dict]:
     
        try:
            # Garante que o repositório de mensagens está inicializado
            self._ensure_repo()
            
            # Busca mensagens do remetente específico para o usuário
            return self.message_repo.get_messages_by_sender(username, sender)
            
        except Exception as e:
            # Trata erros durante a busca
            logger.error(f"Erro ao buscar mensagens de {sender}: {e}")
            return []  # Retorna lista vazia em caso de erro

class SystemService:
    """Serviço principal do sistema."""
    
    def __init__(self):
        """Inicializa o serviço principal."""
        self.user_service = UserService()
        self.message_service = MessageService()
        self.current_user = None
    
    def initialize_system(self) -> bool:
        """
        Inicializa o sistema e conecta ao banco de dados.
        
        Returns:
            bool: True se a inicialização foi bem-sucedida, False caso contrário.
        """
        try:
            # Conecta ao banco de dados
            if not db_manager.connect():
                return False
            
            # Insere dados de mock se necessário
            db_manager.insert_mock_data()
            
            logger.info("Sistema inicializado com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar sistema: {e}")
            return False
    
    def login(self, username: str) -> bool:
      
        try:
            if self.user_service.authenticate_user(username):
                self.current_user = username
                logger.info(f"Usuário {username} fez login com sucesso.")
                return True
            else:
                logger.warning(f"Falha no login do usuário {username}.")
                return False
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return False
    
    def logout(self):
        """Realiza logout do usuário atual."""
        if self.current_user:
            logger.info(f"Usuário {self.current_user} fez logout.")
            self.current_user = None
    
    def get_current_user(self) -> Optional[str]:
       
        return self.current_user
    
    def is_logged_in(self) -> bool:
      
        return self.current_user is not None
    
    def shutdown(self):
        """Encerra o sistema e fecha conexões."""
        try:
            self.logout()
            db_manager.close_connection()
            logger.info("Sistema encerrado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao encerrar sistema: {e}")

# Instância global do serviço principal
system_service = SystemService()

