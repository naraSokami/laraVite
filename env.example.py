import os

VERSION = '1.0.3'
PATH = os.path.expanduser('~') + "/bin/laraVite"

DEFAULT_POLICY_CONDITION = "Auth::user()->role_id === 1"

EVENT_PROVIDER_PATH = "app/Providers/EventServiceProvider.php"

AUTO_SERV=True

MAIL_MAILER='smtp'
MAIL_HOST='smtp.mailtrap.io'
MAIL_PORT='2525'
MAIL_USERNAME='username'
MAIL_PASSWORD='password'
MAIL_ENCRYPTION='tls'