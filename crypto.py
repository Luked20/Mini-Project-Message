"""
Módulo de criptografia para o sistema de mensageria segura.
Implementa criptografia simétrica usando AES-256-GCM.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
import os
import secrets
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoManager:
    """Classe responsável por operações de criptografia e descriptografia."""
    
    def __init__(self):
        """Inicializa o gerenciador de criptografia."""
        self.algorithm = "AES-256-GCM"
        self.key_length = 32  # 256 bits
        self.salt_length = 16  # 128 bits
        self.nonce_length = 12  # 96 bits para GCM
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
      
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=salt,
            iterations=100000,  
        )
        return kdf.derive(password.encode('utf-8'))
    
    def encrypt_message(self, message: str, password: str) -> str:

        if not message or not password:
            raise ValueError("Mensagem e senha não podem estar vazias.")
        
        try:
            # Gera salt aleatório
            salt = os.urandom(self.salt_length)
            
            # Deriva a chave a partir da senha
            key = self._derive_key(password, salt)
            
            # Gera nonce aleatório
            nonce = os.urandom(self.nonce_length)
            
            # Cria instância do AES-GCM
            aesgcm = AESGCM(key)
            
            # Criptografa a mensagem
            ciphertext = aesgcm.encrypt(nonce, message.encode('utf-8'), None)
            
            # Combina salt + nonce + ciphertext
            encrypted_data = salt + nonce + ciphertext
            
            # Codifica em Base64 para armazenamento seguro
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            
            logger.info("Mensagem criptografada com sucesso.")
            return encrypted_b64
            
        except Exception as e:
            logger.error(f"Erro ao criptografar mensagem: {e}")
            raise Exception(f"Falha na criptografia: {str(e)}")
    
    def decrypt_message(self, encrypted_b64: str, password: str) -> str:
    
        if not encrypted_b64 or not password:
            raise ValueError("Dados criptografados e senha não podem estar vazios.")
        
        try:
            # Decodifica do Base64
            encrypted_data = base64.b64decode(encrypted_b64)
            
            # Verifica se os dados têm tamanho mínimo
            min_length = self.salt_length + self.nonce_length
            if len(encrypted_data) < min_length:
                raise ValueError("Dados criptografados inválidos.")
            
            # Extrai salt, nonce e ciphertext
            salt = encrypted_data[:self.salt_length]
            nonce = encrypted_data[self.salt_length:self.salt_length + self.nonce_length]
            ciphertext = encrypted_data[self.salt_length + self.nonce_length:]
            
            # Deriva a chave a partir da senha
            key = self._derive_key(password, salt)
            
            # Cria instância do AES-GCM
            aesgcm = AESGCM(key)
            
            # Descriptografa a mensagem
            decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            decrypted_message = decrypted_bytes.decode('utf-8')
            
            logger.info("Mensagem descriptografada com sucesso.")
            return decrypted_message
            
        except Exception as e:
            logger.error(f"Erro ao descriptografar mensagem: {e}")
            raise Exception("Chave incorreta! Acesso negado.")
    
    def validate_password_strength(self, password: str) -> bool:
     
        if not password:
            return False
        
        # Verifica comprimento mínimo
        if len(password) < 8:
            return False
        
        # Verifica se contém pelo menos uma letra e um número
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_letter and has_digit

# Instância global do gerenciador de criptografia
crypto_manager = CryptoManager()

