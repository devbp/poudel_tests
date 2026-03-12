import logging
import pandas as pd
def logger():
   
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("RTHtestlog.log", mode="w")
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger



def load_params_from_csv(path):
    try:
        df = pd.read_csv(path)
        return list(df.itertuples(index=False, name=None))
    except Exception as e:
        
        raise Exception("Test Data file not found{e}")
