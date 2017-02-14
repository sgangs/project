def allow_gemadmin(user):
    return (user.user_type=='Master' or user.user_type=='Admin' or user.user_type=='Principal')