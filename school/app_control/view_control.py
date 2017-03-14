def allow_admincontrol(user):
    return (user.user_type=='Master' or user.user_type=='Admin' or user.user_type=='Principal')

def allow_admin_teacher(user):
    return (user.user_type=='Master' or user.user_type=='Admin' or user.user_type=='Principal' or user.user_type=='Teacher')

def allow_owner_principal(user):
    return (user.user_type=='Master' or user.user_type=='Principal')  

def allow_staff(user):
    return (user.user_type=='Admin' or user.user_type=='Principal' or user.user_type=='Teacher')