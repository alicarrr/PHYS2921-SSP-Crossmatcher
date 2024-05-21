import logging


def setup_logger():
    """Configure logger which will pipe all output from all files into a single text file.
    Note this system is also compatible with multithreading.

    Returns:
        logger (Logger): logging variable to be called in all dependent files 
        which need their output recorded
    """
    logger = logging.getLogger('ExoplanetLogger')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('out_exoplanets.txt', mode='w')  # Overwrite the file
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

logger = setup_logger()