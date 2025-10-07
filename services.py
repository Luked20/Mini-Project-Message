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
        """
        Autentica um usuário no sistema.
        
        Este método implementa o processo de autenticação de usuário:
        1. Garante que o repositório está inicializado
        2. Valida formato do username (deve começar com @)
        3. Verifica se o usuário existe no banco de dados
        4. Retorna resultado da autenticação
        
        Args:
            username (str): Nome de usuário a ser autenticado.
            
        Returns:
            bool: True se o usuário foi autenticado com sucesso, False caso contrário.
        """
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
        """
        Retorna lista de usuários disponíveis para envio de mensagens.
        
        Este método implementa a busca de usuários disponíveis:
        1. Garante que o repositório está inicializado
        2. Busca todos os usuários cadastrados no sistema
        3. Exclui o usuário atual da lista
        4. Retorna lista de usuários disponíveis
        
        Args:
            current_user (str): Username do usuário atual.
            
        Returns:
            List[Dict]: Lista de usuários disponíveis para envio de mensagens.
        """
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
        """
        Valida se um destinatário existe no sistema.
        
        Este método implementa a validação de destinatário:
        1. Garante que o repositório está inicializado
        2. Valida formato do username (deve começar com @)
        3. Verifica se o destinatário existe no banco de dados
        4. Retorna resultado da validação
        
        Args:
            recipient (str): Username do destinatário a ser validado.
            
        Returns:
            bool: True se o destinatário é válido, False caso contrário.
        """
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
        """
        Envia uma mensagem criptografada.
        
        Este método implementa o processo completo de envio de mensagem:
        1. Garante que o repositório está inicializado
        2. Valida tamanho mínimo da mensagem (50 caracteres)
        3. Valida se o destinatário existe no sistema
        4. Valida força da chave secreta
        5. Criptografa a mensagem usando AES-256-GCM
        6. Salva a mensagem criptografada no banco de dados
        7. Retorna resultado da operação
        
        Args:
            from_user (str): Username do remetente.
            to_user (str): Username do destinatário.
            message (str): Conteúdo da mensagem a ser enviada.
            secret_key (str): Chave secreta para criptografia.
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem de status)
        """
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
        """
        Retorna o número de mensagens não lidas de um usuário.
        
        Este método implementa a contagem de mensagens não lidas:
        1. Garante que o repositório está inicializado
        2. Busca contagem de mensagens com status "unread"
        3. Retorna número de mensagens não lidas
        4. Trata erros retornando 0 em caso de falha
        
        Args:
            username (str): Username do usuário.
            
        Returns:
            int: Número de mensagens não lidas (0 em caso de erro).
        """
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
        """
        Retorna mensagens não lidas agrupadas por remetente.
        
        Este método implementa o agrupamento de mensagens não lidas:
        1. Garante que o repositório está inicializado
        2. Busca todas as mensagens não lidas do usuário
        3. Agrupa mensagens por remetente (from_user)
        4. Retorna dicionário com mensagens agrupadas
        5. Trata erros retornando dicionário vazio
        
        Args:
            username (str): Username do destinatário.
            
        Returns:
            Dict[str, List[Dict]]: Mensagens agrupadas por remetente.
        """
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
        """
        Lê uma mensagem descriptografada.
        
        Este método implementa o processo completo de leitura de mensagem:
        1. Garante que o repositório está inicializado
        2. Busca a mensagem pelo ID
        3. Valida se a mensagem pertence ao usuário
        4. Verifica se a mensagem já foi lida
        5. Tenta descriptografar usando a chave secreta
        6. Marca mensagem como lida se descriptografia for bem-sucedida
        7. Retorna resultado da operação
        
        Args:
            message_id (str): ID da mensagem a ser lida.
            secret_key (str): Chave secreta para descriptografia.
            username (str): Username do destinatário (para validação de acesso).
            
        Returns:
            Tuple[bool, str, str]: (sucesso, mensagem de status, conteúdo descriptografado)
        """
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
        """
        Retorna mensagens de um remetente específico.
        
        Este método implementa a busca de mensagens por remetente:
        1. Garante que o repositório está inicializado
        2. Busca mensagens não lidas de um remetente específico
        3. Retorna lista de mensagens do remetente
        4. Trata erros retornando lista vazia
        
        Args:
            username (str): Username do destinatário.
            sender (str): Username do remetente.
            
        Returns:
            List[Dict]: Lista de mensagens do remetente (lista vazia em caso de erro).
        """
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
        """
        Realiza login de um usuário.
        
        Args:
            username (str): Nome de usuário.
            
        Returns:
            bool: True se o login foi bem-sucedido, False caso contrário.
        """
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
        """
        Retorna o usuário atualmente logado.
        
        Returns:
            Optional[str]: Username do usuário logado ou None.
        """
        return self.current_user
    
    def is_logged_in(self) -> bool:
        """
        Verifica se há um usuário logado.
        
        Returns:
            bool: True se há usuário logado, False caso contrário.
        """
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
