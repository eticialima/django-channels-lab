"""
MANUAL TEST GUIDE FOR SUPPORT SYSTEM
=====================================

Este arquivo guia você através de testes manuais para o sistema de suporte.

SETUP INICIAL
=============
1. Terminal 1 - Redis:
   $ docker compose up -d
   $ docker compose ps  (verificar se está rodando)

2. Terminal 2 - Django:
   $ source ../.venv/Scripts/activate (ou venv\Scripts\activate no Windows)
   $ python manage.py runserver

3. Criar superuser (admin):
   $ python manage.py createsuperuser
   # Digite: username: admin, password: admin123

TEST 1: CLIENTE CONECTA AO SUPORTE
===================================
✓ Passo 1: Abra navegador http://127.0.0.1:8000/support/
✓ Passo 2: Digite seu nome: "João Silva"
✓ Passo 3: Clique "Start Support Chat"
✓ Esperado: Status fica VERDE "Connected"
✓ Esperado: Vê mensagem "You are in queue..."

PROBLEMA ENCONTRADO:
Mensagens não são enviadas via WebSocket. Problema:
- O consumer.receive() não recebe o payload corretamente
- Falta passagem do room_type nas rotas WebSocket

TEST 2: ADMIN VÊ CLIENTE
========================
✓ Passo 1: Abra navegador http://127.0.0.1:8000/support/admin/
✓ Passo 2: Faça login (admin / admin123)
✓ Esperado: Vê "João Silva" na lista de clientes

PROBLEMA ENCONTRADO:
Admin não recebe notificação de novo cliente. Problema:
- Admin group_send não está funcionando
- Falta sincronização entre client_joined e admin dashboard

TEST 3: ENVIAR MENSAGEM
=======================
✓ Passo 1: Cliente escreve: "Olá admin!"
✓ Passo 2: Clica "Send"
✓ Esperado: Mensagem aparece em azul (seu lado)
✓ Passo 3: Admin vê a mensagem em tempo real

PROBLEMA ENCONTRADO:
Mensagens não sincronizam. Investigar:
1. Verificar se socket.send() está enviando JSON correto
2. Verificar em DevTools > Network > WS se payload é enviado
3. Verificar console se há erros JavaScript

DIAGNOSTICAR
============

1. Verificar DevTools (F12) > Console do Cliente:
   - Procure por: "WebSocket error" ou "Chat message received"
   - Se vir erro de conexão, verificar:
     a) Redis está rodando? docker ps
     b) Django está rodando? check http://127.0.0.1:8000/admin/
     c) Migrations foram aplicadas? python manage.py migrate

2. Verificar Django Console (Terminal):
   - Procure por warnings ou errors relacionados a Channels
   - Se houver erro de database, tente: python manage.py migrate --run-syncdb

3. Verificar Admin Database:
   - http://127.0.0.1:8000/admin/chat/clientsession/
   - http://127.0.0.1:8000/admin/chat/message/
   - Se estão vazios, WebSocket não criou registros

CHECKLIST TÉCNICO
=================
- [ ] Redis rodando: docker compose ps
- [ ] Django rodando: http://127.0.0.1:8000/
- [ ] Migrations aplicadas: python manage.py migrate
- [ ] Superuser criado: python manage.py createsuperuser
- [ ] DevTools console limpo (sem erros de conexão)
- [ ] Websocket URL correta: ws://127.0.0.1:8000/ws/support/client/

PRÓXIMOS PASSOS
===============
Se tudo funcionar, implementar:
1. Notificações de som
2. Histórico persistente de chats
3. Typings indicator (mostrando que admin está digitando)
4. Feedback de cliente (rating do atendimento)
5. Campos obrigatórios: email, telefone
"""
