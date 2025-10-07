# 🔐 Sistema de Mensageria Segura

Sistema de linha de comando (CLI) em Python para troca de mensagens seguras entre usuários, utilizando criptografia simétrica AES-256-GCM e MongoDB para persistência de dados.

## 📋 Características

- **Segurança Máxima**: Criptografia AES-256-GCM com chaves derivadas via PBKDF2
- **Chaves Secretas**: Nunca armazenadas no sistema, combinadas verbalmente entre usuários
- **Interface Intuitiva**: CLI moderna e fácil de usar
- **Persistência Robusta**: MongoDB com índices otimizados
- **Arquitetura Limpa**: Separação de responsabilidades em camadas

## 🚀 Instalação

1. **Clone o repositório**:
```bash
git clone <url-do-repositorio>
cd message-mini-project
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Execute o sistema**:
```bash
python main.py
```

## 📖 Como Usar

### 1. Login
- Execute o programa e digite seu @username
- O sistema criará automaticamente usuários de exemplo se necessário

### 2. Menu Principal
Após o login, você terá acesso a:
- **Escrever nova mensagem**: Enviar mensagens criptografadas
- **Ver mensagens não lidas**: Ler mensagens recebidas
- **Listar usuários**: Ver todos os usuários disponíveis
- **Sair**: Encerrar a aplicação

### 3. Enviando Mensagens
1. Escolha "Escrever nova mensagem"
2. Selecione o destinatário da lista
3. Digite sua mensagem (mínimo 50 caracteres)
4. **IMPORTANTE**: Digite a chave secreta combinada verbalmente com o destinatário
5. A mensagem será criptografada e salva no banco

### 4. Lendo Mensagens
1. Escolha "Ver minhas mensagens não lidas"
2. Selecione a mensagem que deseja ler
3. Digite a chave secreta combinada com o remetente
4. Se a chave estiver correta, a mensagem será descriptografada e marcada como lida

## 🔧 Arquitetura

### Estrutura do Projeto
```
message-mini-project/
├── main.py              # Interface CLI e ponto de entrada
├── services.py          # Lógica de negócio
├── repository.py        # Acesso a dados (MongoDB)
├── crypto.py           # Módulo de criptografia
├── database.py         # Configuração e conexão MongoDB
├── requirements.txt    # Dependências do projeto
└── README.md          # Este arquivo
```

### Camadas da Aplicação
- **Apresentação (CLI)**: Interface com o usuário
- **Serviços**: Lógica de negócio e orquestração
- **Repositório**: Acesso aos dados
- **Criptografia**: Operações de segurança

## 🔐 Segurança

### Criptografia
- **Algoritmo**: AES-256-GCM
- **Derivação de Chave**: PBKDF2 com 100.000 iterações
- **Salt**: 128 bits aleatório por mensagem
- **Nonce**: 96 bits aleatório por mensagem

### Boas Práticas
- Chaves secretas nunca são armazenadas
- Validação de força das chaves
- Tratamento robusto de erros
- Logs detalhados para auditoria

## 📊 Banco de Dados

### Estrutura MongoDB
- **Banco**: `chat`
- **Coleções**:
  - `users`: Informações dos usuários
  - `messages`: Mensagens criptografadas

### Índices
- `username` (único) na coleção `users`
- `(to_user, status)` na coleção `messages`
- `from_user` e `sent_at` na coleção `messages`

## 🛠️ Desenvolvimento

### Dependências
- `pymongo==4.6.0`: Driver MongoDB
- `cryptography==41.0.7`: Criptografia AES
- `python-dotenv==1.0.0`: Gerenciamento de variáveis

### Logs
O sistema gera logs detalhados em:
- Console (nível INFO)
- Arquivo `messageria.log`

## ⚠️ Importante

1. **Chaves Secretas**: Sempre combine as chaves verbalmente com o destinatário
2. **Segurança**: Nunca compartilhe chaves por mensagens não criptografadas
3. **Backup**: As mensagens são armazenadas criptografadas no MongoDB
4. **Rede**: Certifique-se de ter conexão com a internet para acessar o MongoDB

## 🐛 Solução de Problemas

### Erro de Conexão MongoDB
- Verifique sua conexão com a internet
- Confirme se a string de conexão está correta

### Erro de Criptografia
- Verifique se a chave secreta está correta
- Certifique-se de que a chave tem pelo menos 8 caracteres
- A chave deve conter letras e números

### Mensagem Não Encontrada
- Verifique se o ID da mensagem está correto
- Confirme se a mensagem pertence ao usuário logado

## 📝 Licença

Este projeto é desenvolvido para fins educacionais e de demonstração.

---

**Desenvolvido com ❤️ usando Python, MongoDB e criptografia de ponta.**
