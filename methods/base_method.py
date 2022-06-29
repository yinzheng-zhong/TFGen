import pandas as pd


class BaseMethod:
    def __init__(self, window_size: int, input_stream, output_stream):
        self.window_size = window_size
        self.input_stream = input_stream
        self.output_stream = output_stream

        self.event_log = None
        self.case_id_col = None
        self.attributes_cols = None

    def init_window(self):
        raise NotImplementedError

    def start_processing(self):
        raise NotImplementedError
