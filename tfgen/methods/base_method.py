from collections import deque

import pandas as pd
import numpy as np
from tfgen import const
from tfgen.models.tet import TET


class BaseMethod:
    def __init__(self, ec_lookup_table, window_size, input_stream, output_stream):
        self.ec_lookup_table = ec_lookup_table
        self.window_size = window_size
        self.input_stream = input_stream
        self.output_stream = output_stream

        self.tet = TET()
        self.sliding_window_buffer = deque(maxlen=self.window_size)

        self.event_log = None
        self.case_id_col = None
        self.attributes_cols = None

        self.current_case = None

        _len_lookup = len(ec_lookup_table)
        self.transition_counts = np.zeros((_len_lookup, _len_lookup), dtype=np.float)

    def index_lookup(self, ec):
        try:
            return self.ec_lookup_table[ec]
        except KeyError:
            return self.ec_lookup_table[const.TOKEN_DEFAULT]

    def start_processing(self):
        raise NotImplementedError
