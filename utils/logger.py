import logging
import os
import sys
from datetime import datetime
from .constants import USERNAME, LOG_PATH

class UTF8StreamHandler(logging.StreamHandler):
    def emit(self, record):
        msg = self.format(record)
        msg = msg.encode("utf-8")
        stream = self.stream
        stream.write(msg.decode("utf-8"))
        stream.write(self.terminator)
        self.flush()
        
class Logger:
    
    LOGGER_NAME = USERNAME
    FORMAT_DEFAULT = "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
    FILE_FORMAT_DEFAULT = "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
    SECONDS_FMT_DEF = r"%Y-%m-%d %H:%M:%S"
    LEVEL_DEFAULT = logging.DEBUG
    LEVEL_WRITE_DEFAULT = logging.WARNING
    PROPAGATE_DEFAULT = False
    
    _logger = None
    
    @classmethod
    def logger(cls):
        
        if not cls._logger:
            
            if cls.logger_exists():
                cls._logger = logging.getLogger(cls.LOGGER_NAME)
                
            else:
                cls._logger = logging.getLogger(cls.LOGGER_NAME)
                cls._logger.setLevel(cls.LEVEL_DEFAULT)
                cls._logger.propagate = cls.PROPAGATE_DEFAULT
            
                formatter = logging.Formatter(cls.FORMAT_DEFAULT, cls.SECONDS_FMT_DEF)

                #handler = logging.StreamHandler(sys.stderr)
                handler = UTF8StreamHandler(sys.stderr)
                handler.setFormatter(formatter)
                
                cls._logger.addHandler(handler)
        
        return cls._logger
        
    @classmethod
    def logger_exists(cls):
        return cls.LOGGER_NAME in logging.Logger.manager.loggerDict.keys()
    
    @classmethod
    def set_level(cls, level):
        logger = cls.logger()
        logger.setLevel(level)
        
    @classmethod
    def set_propagate(cls, propagate):
        logger = cls.logger()
        logger.propagate = propagate
       
    @classmethod
    def debug(cls, msg, *args, **kwargs):
        logger = cls.logger()
        logger.debug(msg, *args, **kwargs)
        
    @classmethod
    def info(cls, msg, *args, **kwargs):
        logger = cls.logger()
        logger.info(msg, *args, **kwargs)
        
    @classmethod
    def warning(cls, msg, *args, **kwargs):
        logger = cls.logger()
        logger.warning(msg, *args, **kwargs)
        
    @classmethod
    def error(cls, msg, *args, **kwargs):
        logger = cls.logger()
        logger.error(msg, *args, **kwargs)
        
    @classmethod
    def critical(cls, msg, *args, **kwargs):
        logger = cls.logger()
        logger.critical(msg, *args, **kwargs)
        
    @classmethod
    def log(cls, level, msg, *args, **kwargs):
        logger = cls.logger()
        logger.log(level, msg, *args, **kwargs)
        
    @classmethod
    def exception(cls, msg, *args, **kwargs):
        logger = cls.logger()
        logger.exception(msg, *args, **kwargs)
        
    @classmethod
    def write_to_file(cls, path, level = LEVEL_WRITE_DEFAULT):
        file_handler = logging.FileHandler(path)
        file_handler.setLevel(level)
        
        formatter = logging.Formatter(cls.FILE_FORMAT_DEFAULT, cls.SECONDS_FMT_DEF)
        file_handler.setFormatter(formatter)
        
        logger = cls.logger()
        logger.addHandler(file_handler)
        
def log_filename(current_file = None):
    """_summary_

    Args:
        current_file (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime(r"%Y_%m_%d")
    
    if current_file:
        return f"{formatted_datetime}.{USERNAME}.{current_file}.log"
    else:
        return f"{formatted_datetime}.{USERNAME}.log"
    
def log_filepath():
    
    return os.path.join(LOG_PATH, log_filename())