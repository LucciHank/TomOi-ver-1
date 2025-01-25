def mask_email(email):
    """
    Mask email address:
    hoanganhdo182@gmail.com → h****2@gmail.com
    """
    if not email or '@' not in email:
        return email
        
    local_part, domain = email.split('@')
    
    if len(local_part) <= 2:
        return f"{local_part}@{domain}"
        
    masked = f"{local_part[0]}{'*' * (len(local_part)-2)}{local_part[-1]}@{domain}"
    return masked 