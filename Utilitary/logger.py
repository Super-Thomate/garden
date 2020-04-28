import typing
from datetime import datetime


def log(source: str, to_log: str, output_file: typing.Optional[str] = None):
    """
    Log information in explicit format

    :param source: str | Where the log comes from. Expected format: `module::function`
    :param to_log: str | The information to be logged
    :param output_file: str or None | The file to open where the log
    should be written, if none provided write in STDOUT
    """
    log_text = f"[{datetime.now().strftime('%m/%d/%Y %H:%M:%S')}] {source} : {to_log}"
    if output_file is not None:
        with open(output_file, 'a', encoding='utf-8') as file:
            file.write(log_text)
    else:
        print(log_text)
