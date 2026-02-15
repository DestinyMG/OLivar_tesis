from django.core.mail import send_mail
from django.conf import settings

def enviar_correo_codigo(email_destino, codigo):
    asunto = 'Código de Verificación - Recuperación de Contraseña'
    mensaje = f'''
    Has solicitado restablecer tu contraseña en el Sistema de Incidencias.
    
    Tu código de verificación es: {codigo}
    
    Este código es válido por 10 minutos. Si no solicitaste esto, ignora este mensaje.
    '''
    try:
        send_mail(
            asunto,
            mensaje,
            settings.EMAIL_HOST_USER,
            [email_destino],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False