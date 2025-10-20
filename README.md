# 🧠 FlashSale Reservation System

> Sistema de reserva de produtos com consistência transacional utilizando o **padrão Outbox**, **RabbitMQ**, **FastAPI** e **PostgreSQL**.  
> O projeto demonstra uma arquitetura event-driven moderna, com workers distribuídos e comunicação assíncrona confiável.

---

## 🏗️ Desenho da Solução

![Arquitetura](image-1.png)

### 🔹 Fluxo resumido
1. O serviço de **Reserva (FastAPI)** grava a reserva e um evento `ReservationPending` na tabela `outbox`.
2. O **Outbox Worker** lê os eventos pendentes e publica no **RabbitMQ**.
3. O RabbitMQ entrega as mensagens para os **Workers de Confirmação** e **Expiração**, que processam e atualizam o banco.
4. O **Redis** é utilizado como cache para consultas de estoque.

---

## 🧩 Modelagem de Dados

| Tabela        | Descrição                                                                 |
|----------------|--------------------------------------------------------------------------|
| `product`      | Cadastro de produtos                                                     |
| `inventory`    | Estoque, com colunas `total`, `reserved` e `available`                   |
| `reservation`  | Reservas criadas pelos usuários com status `pending`, `confirmed`, etc. |
| `outbox`       | Eventos pendentes ou publicados, garantindo consistência eventual        |
| `user`         | Usuários da plataforma                                                   |
| `orders`       | (em desenvolvimento) Geração da ordem de compra após confirmação         |
| `payment`      | (em desenvolvimento) Simulação de gateway de pagamento                   |

---

## 🧱 Arquitetura Técnica

| Componente | Descrição |
|-------------|-----------|
| **FastAPI** | API de reservas e pagamentos |
| **RabbitMQ** | Message Broker para eventos assíncronos |
| **PostgreSQL** | Banco relacional para dados e outbox |
| **Redis** | Cache de estoque |
| **Outbox Worker** | Publica eventos do banco no RabbitMQ |
| **Worker Confirmação** | Processa `payment.approved` e confirma reservas |
| **Worker Expiração** | Monitora expiração e libera estoque |

---

## 🚀 Como Rodar

### Pré-requisitos
- Docker e Docker Compose instalados.

### Subir ambiente
```bash
docker-compose up --build -d
