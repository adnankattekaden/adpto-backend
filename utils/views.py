from datetime import datetime, timedelta

import decouple
import jwt


class TokenGenerate:
    def generate(self, user):
        if user is not None:
            access_expiry_time = datetime.now() + timedelta(seconds=1800)  # 30 minutes
            access_expiry = access_expiry_time.strftime("%d/%m/%Y %H:%M:%S")
            access_token = jwt.encode(
                {'id': user.id, 'expiry': access_expiry, 'tokenType': 'access'},
                decouple.config('SECRET_KEY'),
                algorithm="HS256")

            refresh_expiry_time = datetime.now() + timedelta(seconds=259200)  # 3 days
            refresh_expiry = refresh_expiry_time.strftime("%d/%m/%Y %H:%M:%S")
            refresh_token = jwt.encode(
                {'id': user.id, 'expiry': refresh_expiry, 'tokenType': 'refresh'},
                decouple.config('SECRET_KEY'),
                algorithm="HS256")
            auth = {'accessToken': access_token, 'refreshToken': refresh_token, 'expiry': access_expiry}
        else:
            auth = None
        return auth
