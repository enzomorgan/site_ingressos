from django.core.mail import EmailMessage

def send_tickets_email(order):
    user = order.user
    tickets = order.tickets.all()
    
    if not user.email:
        return
    
    if not tickets.exists():
        return
    
    subject = f'Seus ingressos do pedido #{order.id}'
    
    body = (
        f'Olá, {user.first_name or user.username}!\n\n'
        f'Seu pagamento do pedido #{order.id} foi confirmado.\n'
        f'Seus ingressos estão anexados neses e-mail em formato PDF.\n\n'
        f'Você também pode acessar seus ingressos pelo site, na área "Meus ingressos.\n\n'
        f'Obrigado pela compra!'
    )
    
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=None,
        to=[user.email],
    )
    
    for ticket in tickets:
        if ticket.pdf_file:
            email.attach_file(ticket.pdf_file.path)
            
    email.send(fail_silently=False)