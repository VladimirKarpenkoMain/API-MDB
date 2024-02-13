from django.core.mail import send_mail


def sent_confirmation_code(email: str, confirmation_code: str) -> None:
    """ Oтправляет на почту пользователя код подтверждения."""
    send_mail(
        subject="Код подтверждения вашего аккаунта",
        message=f"Ваш код подтверждения: {confirmation_code}",
        from_email=None,
        recipient_list=(email,),
    )
