
import sys
import os
from typing import List, Dict, Optional
import logging

from services import system_service

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('messageria.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MessageriaCLI:
    """Classe principal da interface de linha de comando."""
    
    def __init__(self):
        """Inicializa a CLI."""
        self.running = True
    
    def clear_screen(self):
        """Limpa a tela do terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Imprime o cabeçalho da aplicação."""
        print("=" * 60)
        print("SISTEMA DE MENSAGERIA SEGURA")
        print("=" * 60)
        print()
    
    def print_separator(self):
        """Imprime um separador visual."""
        print("-" * 60)
    
    def wait_for_enter(self):
        """Aguarda o usuário pressionar Enter."""
        input("\nPressione Enter para continuar...")
    
    def get_user_input(self, prompt: str, required: bool = True) -> str:
      
        while True:  # Loop infinito até obter entrada válida
            try:
                # Captura entrada do usuário e remove espaços nas extremidades
                user_input = input(prompt).strip()
                
                # Verifica se campo é obrigatório e está vazio
                if required and not user_input:
                    print("ERRO: Este campo é obrigatório. Tente novamente.")
                    continue  # Volta ao início do loop
                
                # Retorna entrada válida
                return user_input
                
            except KeyboardInterrupt:
                # Trata interrupção do teclado (Ctrl+C)
                print("\n\nOperação cancelada pelo usuário.")
                return ""  # Retorna string vazia indicando cancelamento
                
            except Exception as e:
                # Trata qualquer outro erro de entrada
                print(f"ERRO na entrada: {e}")
                return ""  # Retorna string vazia indicando erro
    
    def show_login_screen(self) -> bool:
    
        # Limpa a tela do terminal para uma interface limpa
        self.clear_screen()
        
        # Exibe cabeçalho da aplicação
        self.print_header()
        
        # Exibe título da tela de login
        print("TELA DE LOGIN")
        print()
        
        # Loop principal de autenticação
        while True:
            # Solicita username do usuário
            username = self.get_user_input("Digite seu @username: ")
            
            # Verifica se usuário cancelou a operação
            if not username:
                return False  # Retorna False indicando cancelamento
            
            # Valida formato do username (deve começar com @)
            if not username.startswith('@'):
                print("ERRO: O username deve começar com @ (ex: @usuario)")
                continue  # Volta ao início do loop para nova tentativa
            
            # Exibe mensagem de autenticação em andamento
            print(f"\nAutenticando {username}...")
            
            # Tenta fazer login do usuário no sistema
            if system_service.login(username):
                # Login bem-sucedido
                print(f"SUCESSO: Login realizado com sucesso! Bem-vindo, {username}")
                self.wait_for_enter()  # Pausa para usuário ver a mensagem
                return True  # Retorna True indicando sucesso
            else:
                # Login falhou - usuário não encontrado
                print(f"ERRO: Usuário {username} não encontrado.")
                
                # Pergunta se usuário quer tentar novamente
                retry = self.get_user_input("Deseja tentar novamente? (s/n): ", required=False)
                
                # Verifica resposta do usuário
                if retry.lower() not in ['s', 'sim', 'y', 'yes']:
                    return False  # Usuário escolheu não tentar novamente
    
    def show_main_menu(self):
   
        # Limpa a tela para uma interface limpa
        self.clear_screen()
        
        # Exibe cabeçalho da aplicação
        self.print_header()
        
        # Obtém usuário atualmente logado
        current_user = system_service.get_current_user()
        
        # Conta mensagens não lidas do usuário atual
        unread_count = system_service.message_service.get_unread_messages_count(current_user)
        
        # Exibe informações do usuário logado
        print(f"Usuário logado: {current_user}")
        print(f"Mensagens não lidas: {unread_count}")
        print()
        
        # Exibe título do menu principal
        print("MENU PRINCIPAL")
        self.print_separator()  # Linha separadora visual
        
        # Lista todas as opções disponíveis no menu
        print("1. Escrever nova mensagem")
        print("2. Ver minhas mensagens não lidas")
        print("3. Listar usuários disponíveis")
        print("4. Sair")
        print()
    
    def show_write_message(self):
     
        # Limpa a tela para interface limpa
        self.clear_screen()
        
        # Exibe cabeçalho da aplicação
        self.print_header()
        
        # Exibe título da funcionalidade
        print("ESCREVER NOVA MENSAGEM")
        self.print_separator()
        
        # Obtém usuário atualmente logado
        current_user = system_service.get_current_user()
        
        # Lista usuários disponíveis para envio de mensagens
        print("Usuários disponíveis:")
        users = system_service.user_service.get_available_users(current_user)
        
        # Verifica se há usuários disponíveis
        if not users:
            print("ERRO: Nenhum usuário disponível para envio de mensagens.")
            self.wait_for_enter()
            return  # Encerra função se não há usuários
        
        # Exibe lista numerada de usuários disponíveis
        for i, user in enumerate(users, 1):
            print(f"  {i}. {user['username']}")
        
        print()  # Linha em branco para separação visual
        
        # Loop para seleção do destinatário
        while True:
            try:
                # Solicita escolha do destinatário
                choice = self.get_user_input("Escolha o número do destinatário: ")
                
                # Verifica se usuário cancelou
                if not choice:
                    return  # Encerra função se cancelado
                
                # Converte escolha para número inteiro
                choice_num = int(choice)
                
                # Valida se escolha está dentro do range válido
                if 1 <= choice_num <= len(users):
                    # Seleciona destinatário baseado na escolha
                    recipient = users[choice_num - 1]['username']
                    break  # Sai do loop se escolha válida
                else:
                    # Exibe erro se escolha fora do range
                    print(f"ERRO: Escolha inválida. Digite um número entre 1 e {len(users)}")
                    
            except ValueError:
                # Trata erro de conversão para inteiro
                print("ERRO: Digite um número válido.")
            except KeyboardInterrupt:
                # Trata interrupção do teclado
                return  # Encerra função se interrompido
        
        # Seção de entrada da mensagem
        print(f"\nEnviando mensagem para {recipient}")
        print("INFORMACAO: A mensagem deve ter pelo menos 50 caracteres.")
        
        # Loop para entrada da mensagem com validação de tamanho
        while True:
            # Solicita conteúdo da mensagem
            message = self.get_user_input("Digite sua mensagem: ")
            
            # Verifica se usuário cancelou
            if not message:
                return  # Encerra função se cancelado
            
            # Valida tamanho mínimo da mensagem
            if len(message) < 50:
                print(f"ERRO: Mensagem muito curta. Mínimo: 50 caracteres. Atual: {len(message)}")
                continue  # Volta ao início do loop
            break  # Sai do loop se mensagem válida
        
        # Seção de entrada da chave secreta
        print("\nCHAVE SECRETA")
        print("INFORMACAO: Esta chave deve ser combinada verbalmente com o destinatário.")
        print("INFORMACAO: A chave deve ter pelo menos 8 caracteres, contendo letras e números.")
        
        # Solicita chave secreta
        secret_key = self.get_user_input("Digite a chave secreta: ")
        
        # Verifica se usuário cancelou
        if not secret_key:
            return  # Encerra função se cancelado
        
        # Processo de envio da mensagem
        print(f"\nEnviando mensagem para {recipient}...")
        
        # Chama serviço para enviar mensagem criptografada
        success, status_message = system_service.message_service.send_message(
            current_user, recipient, message, secret_key
        )
        
        # Exibe resultado do envio
        if success:
            print(f"SUCESSO: {status_message}")
        else:
            print(f"ERRO: {status_message}")
        
        # Pausa para usuário ver o resultado
        self.wait_for_enter()
    
    def show_unread_messages(self):
     
        # Limpa a tela para interface limpa
        self.clear_screen()
        
        # Exibe cabeçalho da aplicação
        self.print_header()
        
        # Exibe título da funcionalidade
        print("MENSAGENS NAO LIDAS")
        self.print_separator()
        
        # Obtém usuário atualmente logado
        current_user = system_service.get_current_user()
        
        # Busca mensagens não lidas agrupadas por remetente
        grouped_messages = system_service.message_service.get_unread_messages_grouped(current_user)
        
        # Verifica se há mensagens não lidas
        if not grouped_messages:
            print("INFORMACAO: Nenhuma mensagem não lida encontrada.")
            self.wait_for_enter()
            return  # Encerra função se não há mensagens
        
        # Converte mensagens agrupadas em lista linear para exibição
        message_list = []
        for sender, messages in grouped_messages.items():
            # Adiciona cada mensagem do remetente à lista
            for i, message in enumerate(messages):
                message_list.append((sender, message, i + 1))
        
        # Exibe contagem de mensagens encontradas
        print(f"Encontradas {len(message_list)} mensagens não lidas:")
        print()
        
        # Exibe lista numerada de mensagens com informações básicas
        for i, (sender, message, msg_num) in enumerate(message_list, 1):
            # Formata data/hora de envio para exibição
            sent_time = message['sent_at'].strftime("%d/%m/%Y %H:%M")
            print(f"{i}. Mensagem de {sender} (enviada em {sent_time})")
        
        print()  # Linha em branco para separação visual
        
        # Loop para seleção da mensagem para leitura
        while True:
            try:
                # Solicita escolha da mensagem
                choice = self.get_user_input("Escolha o número da mensagem para ler (0 para voltar): ")
                
                # Verifica se usuário cancelou
                if not choice:
                    return  # Encerra função se cancelado
                
                # Converte escolha para número inteiro
                choice_num = int(choice)
                
                # Verifica se usuário escolheu voltar
                if choice_num == 0:
                    return  # Encerra função se escolheu voltar
                elif 1 <= choice_num <= len(message_list):
                    # Seleciona mensagem baseada na escolha
                    sender, message, msg_num = message_list[choice_num - 1]
                    # Chama método para ler a mensagem selecionada
                    self.read_message(message, sender)
                    break  # Sai do loop após ler mensagem
                else:
                    # Exibe erro se escolha fora do range
                    print(f"ERRO: Escolha inválida. Digite um número entre 0 e {len(message_list)}")
                    
            except ValueError:
                # Trata erro de conversão para inteiro
                print("ERRO: Digite um número válido.")
            except KeyboardInterrupt:
                # Trata interrupção do teclado
                return  # Encerra função se interrompido
    
    def read_message(self, message: Dict, sender: str):
      
        # Exibe cabeçalho da leitura de mensagem
        print(f"\nLENDO MENSAGEM DE {sender}")
        print("INFORMACAO: Digite a chave secreta combinada com este remetente.")
        
        # Solicita chave secreta do usuário
        secret_key = self.get_user_input("Chave secreta: ")
        
        # Verifica se usuário cancelou
        if not secret_key:
            return  # Encerra função se cancelado
        
        # Exibe mensagem de processamento
        print("\nDescriptografando mensagem...")
        
        # Chama serviço para ler e descriptografar mensagem
        success, status_message, decrypted_content = system_service.message_service.read_message(
            str(message['_id']), secret_key, system_service.get_current_user()
        )
        
        # Verifica resultado da descriptografia
        if success:
            # Descriptografia bem-sucedida
            print("SUCESSO: Mensagem descriptografada com sucesso!")
            print()
            print("CONTEUDO DA MENSAGEM:")
            print("=" * 50)
            print(decrypted_content)  # Exibe conteúdo descriptografado
            print("=" * 50)
        else:
            # Falha na descriptografia (chave incorreta)
            print(f"ERRO: {status_message}")
        
        # Pausa para usuário ver o resultado
        self.wait_for_enter()
    
    def show_available_users(self):
        """
        Exibe lista de usuários disponíveis para envio de mensagens.
        
        Este método implementa a funcionalidade de listagem de usuários:
        1. Busca todos os usuários cadastrados no sistema
        2. Exclui o usuário atual da lista
        3. Exibe informações básicas de cada usuário
        4. Mostra data de cadastro para referência
        
        A lista é útil para o usuário saber quais contatos estão disponíveis
        para envio de mensagens antes de usar a funcionalidade de envio.
        """
        # Limpa a tela para interface limpa
        self.clear_screen()
        
        # Exibe cabeçalho da aplicação
        self.print_header()
        
        # Exibe título da funcionalidade
        print("USUARIOS DISPONIVEIS")
        self.print_separator()
        
        # Obtém usuário atualmente logado
        current_user = system_service.get_current_user()
        
        # Busca lista de usuários disponíveis (excluindo o usuário atual)
        users = system_service.user_service.get_available_users(current_user)
        
        # Verifica se há usuários disponíveis
        if not users:
            print("ERRO: Nenhum usuário disponível.")
        else:
            # Exibe contagem de usuários encontrados
            print(f"Encontrados {len(users)} usuários:")
            print()
            
            # Lista cada usuário com informações básicas
            for i, user in enumerate(users, 1):
                # Formata data de cadastro para exibição
                created_at = user['created_at'].strftime("%d/%m/%Y")
                print(f"{i}. {user['username']} (cadastrado em {created_at})")
        
        # Pausa para usuário ver a lista
        self.wait_for_enter()
    
    def run(self):
        """
        Executa o loop principal da aplicação.
        
        Este método implementa o fluxo principal da aplicação:
        1. Inicializa o sistema e conecta ao banco de dados
        2. Exibe tela de login e autentica usuário
        3. Executa loop principal com menu de opções
        4. Processa escolhas do usuário
        5. Gerencia encerramento da aplicação
        
        Tratamento de erros:
        - Erros de inicialização do sistema
        - Falhas de autenticação
        - Erros no loop principal
        - Interrupções do usuário (Ctrl+C)
        - Erros críticos gerais
        """
        try:
            # Inicializa o sistema e conecta ao banco de dados
            print("Inicializando sistema...")
            if not system_service.initialize_system():
                print("ERRO: Erro ao inicializar sistema. Verifique a conexão com o banco de dados.")
                return  # Encerra aplicação se inicialização falhar
            
            # Exibe tela de login e tenta autenticar usuário
            if not self.show_login_screen():
                print("Encerrando aplicação...")
                return  # Encerra aplicação se login falhar
            
            # Loop principal da aplicação
            while self.running:
                try:
                    # Exibe menu principal com opções disponíveis
                    self.show_main_menu()
                    
                    # Solicita escolha do usuário
                    choice = self.get_user_input("Escolha uma opção: ")
                    
                    # Processa escolha do usuário
                    if choice == "1":
                        # Opção 1: Escrever nova mensagem
                        self.show_write_message()
                    elif choice == "2":
                        # Opção 2: Ver mensagens não lidas
                        self.show_unread_messages()
                    elif choice == "3":
                        # Opção 3: Listar usuários disponíveis
                        self.show_available_users()
                    elif choice == "4":
                        # Opção 4: Sair da aplicação
                        print("Encerrando aplicação...")
                        break  # Sai do loop principal
                    else:
                        # Opção inválida
                        print("ERRO: Opção inválida. Tente novamente.")
                        self.wait_for_enter()  # Pausa para usuário ver erro
                        
                except KeyboardInterrupt:
                    # Trata interrupção do teclado (Ctrl+C)
                    print("\n\nEncerrando aplicação...")
                    break  # Sai do loop principal
                except Exception as e:
                    # Trata erros inesperados no loop principal
                    print(f"ERRO: Erro inesperado: {e}")
                    logger.error(f"Erro no loop principal: {e}")
                    self.wait_for_enter()  # Pausa para usuário ver erro
        
        except Exception as e:
            # Trata erros críticos gerais
            print(f"ERRO: Erro crítico: {e}")
            logger.error(f"Erro crítico: {e}")
        finally:
            # Sempre executa encerramento do sistema
            system_service.shutdown()

def main():
    """
    Função principal da aplicação.
    
    Esta função é o ponto de entrada da aplicação e implementa:
    1. Criação da instância da CLI
    2. Execução do loop principal
    3. Tratamento de erros fatais
    4. Encerramento limpo da aplicação
    
    Tratamento de erros:
    - Interrupção do usuário (Ctrl+C)
    - Erros fatais gerais
    - Encerramento com código de erro apropriado
    """
    try:
        # Cria instância da interface de linha de comando
        cli = MessageriaCLI()
        
        # Executa o loop principal da aplicação
        cli.run()
        
    except KeyboardInterrupt:
        # Trata interrupção do usuário (Ctrl+C)
        print("\n\nAplicacao encerrada pelo usuario.")
    except Exception as e:
        # Trata erros fatais gerais
        print(f"ERRO: Erro fatal: {e}")
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)  # Encerra com código de erro

if __name__ == "__main__":
    main()
