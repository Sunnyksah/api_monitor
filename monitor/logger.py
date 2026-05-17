import logging
import os
from logging.handlers import RotatingFileHandler

os.makedirs("logs", exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter(
         "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
          datefmt="%Y-%m-%d %H:%M:%S"
    )

    #console handler

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    #Rotating file handler (5 MB max, 3 backups)
    fh = RotatingFileHandler("logs/monitor.log", maxBytes=5_000_000, backupCount=3)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
