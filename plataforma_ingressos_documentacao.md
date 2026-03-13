# Plataforma de Venda de Ingressos

Sistema web para divulgação e venda de ingressos de eventos, com geração
automática de QR Code e PDF.

## Visão Geral

A plataforma permite que o administrador cadastre eventos e os usuários
possam: - visualizar eventos - comprar ingressos - receber ingresso com
QR Code - baixar ingresso em PDF - validar ingresso no evento

## Tecnologias

-   Python
-   Django
-   Django Admin
-   PostgreSQL (planejado)
-   QR Code
-   ReportLab (PDF)
-   Stripe (planejado)

## Arquitetura

ticket_platform/ - users - events - tickets - orders - payments
(planejado) - config (settings, urls) - manage.py

## Modelos Criados

### User

Usuário customizado baseado em AbstractUser.

### Event

Campos: - title - slug - description - date - location - banner -
created_by - created_at - active

### TicketType

Tipos de ingressos: - Pista - VIP - Camarote

Campos: - event - name - price - quantity - sold

### Order

Representa uma compra.

Campos: - user - status (pending, paid, canceled) - total - created_at

### OrderItem

Itens dentro do pedido.

Campos: - order - ticket_type - quantity - price

### Ticket

Ingresso individual.

Campos: - order - code (UUID) - qr_code - pdf_file - checked_in -
created_at

## Funcionalidades Implementadas

-   Custom User Model
-   Sistema de eventos
-   Tipos de ingressos
-   Sistema de pedidos
-   Ingressos com UUID
-   Geração automática de QR Code
-   Geração automática de PDF
-   Administração via Django Admin

## Estrutura de Arquivos Gerados

media/ - tickets/ - qrcodes/ - pdfs/

## Fluxo Atual

Admin cria evento ↓ Admin define tipos de ingresso ↓ Usuário realiza
compra ↓ Sistema cria pedido ↓ Sistema gera ingressos ↓ QR Code gerado ↓
PDF gerado

## Funcionalidades Ainda Não Implementadas

### API REST

Endpoints planejados: - GET /events - GET /events/{slug} - POST /orders

### Sistema de Pagamento

Integração planejada com Stripe.

Fluxo: criar pedido → checkout → webhook → pedido pago → gerar ingressos

### Modelo Payment

Campos planejados: - order - transaction_id - gateway - status -
created_at

### Envio de Email

Enviar PDF do ingresso ao usuário após pagamento.

### Sistema de Check-in

Endpoint: POST /checkin/{qr_code}

Fluxo: QR escaneado → validar ingresso → marcar checked_in

### Frontend

Interface para: - listar eventos - visualizar evento - comprar
ingressos - histórico de pedidos

Tecnologias sugeridas: - React - Next.js

### Dashboard do Organizador

-   ingressos vendidos
-   receita
-   check-ins
-   ingressos restantes

## Arquitetura Final Planejada

Frontend ↓ API REST (Django) ↓ PostgreSQL ↓ Stripe

## Próximos Passos

1.  Criar modelo Payment
2.  Integrar Stripe
3.  Gerar ingressos após confirmação de pagamento
4.  Criar API REST
5.  Criar sistema de check-in
6.  Criar frontend

## Status Atual

Projeto em fase de MVP funcional do backend.
