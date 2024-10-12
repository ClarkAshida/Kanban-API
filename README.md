
# Kanban API

## Descrição do Projeto

Este é um projeto de API para gerenciar um sistema de **quadro Kanban**, permitindo que os usuários criem e gerenciem **colunas**, **cartões** e **tarefas**. A API foi construída usando **Django** e **Django Rest Framework (DRF)**, oferecendo uma estrutura robusta para manipular dados e interações com o backend.

## Funcionalidades

- **Criação e gerenciamento de colunas**: Colunas podem ser criadas, editadas e removidas, representando diferentes fases do fluxo de trabalho.
- **Criação e gerenciamento de cartões**: Cartões representam as unidades de trabalho que transitam pelas colunas.
- **Criação e gerenciamento de tarefas**: Cada cartão pode ter várias tarefas associadas, que podem ser concluídas individualmente.
- **Atribuição de usuários aos cartões e tarefas**.

## Requisitos de Instalação

Antes de instalar e rodar o projeto, certifique-se de ter os seguintes componentes:

- **Python 3.8+**
- **Django 3.2+**
- **Django Rest Framework 3.12+**

## Passos de Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/kanban-api.git
cd kanban-api
```

### 2. Criar um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Aplicar as migrações do banco de dados

```bash
python manage.py migrate
```

### 5. Rodar o servidor de desenvolvimento

```bash
python manage.py runserver
```

## Tecnologias Utilizadas

- **Django**: Framework web usado para desenvolvimento rápido e seguro.
- **Django Rest Framework (DRF)**: Framework poderoso para construir APIs web.
- **SQLite**: Banco de dados simples e leve para desenvolvimento.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto é licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
