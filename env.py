import os

VERSION = '1.0.3'
PATH = os.path.expanduser('~') + "/bin/laraVite" + VERSION

DEFAULT_POLICY_CONDITION = "Auth::user()->role_id === 1"

MAIL_MAILER='smtp'
MAIL_HOST='smtp.mailtrap.io'
MAIL_PORT='2525'
MAIL_USERNAME='07722a7d18ff2d'
MAIL_PASSWORD='da0f3830a8ec99'
MAIL_ENCRYPTION='tls'