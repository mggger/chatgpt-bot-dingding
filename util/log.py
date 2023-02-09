import logging
from logging.config import dictConfig

logging_config = dict(
    version=1,
    formatters={
        'f': {'format':
                  '%(asctime)s %(levelname)-8s %(module)-12s[%(lineno)d] %(message)s'}
    },
    handlers={
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG}
    },
    root={
        'handlers': ['h'],
        'level': logging.INFO,
    },
)

dictConfig(logging_config)

logger = logging.getLogger()
