from collections import deque

import pandas as pd
import numpy as np
from tfgen import const
from tfgen.models.tet import TET


class BaseMethod:
    def __init__(self, ec_lookup_table, window_size, input_stream, output_stream):
        self.ec_lookup_table = ec_lookup_table
        self.window_size = window_size
        self._input_stream = input_stream
        self._output_stream = output_stream

        self.tet = TET()
        self.sliding_window_buffer = deque(maxlen=self.window_size)

        self.event_log = None
        self.case_id_col = None
        self.attributes_cols = None

        self.current_case = None

        self.finished = False

        _len_lookup = len(ec_lookup_table)
        self.transition_counts = np.zeros((_len_lookup, _len_lookup), dtype=np.float32)

    def index_lookup(self, ec):
        try:
            return self.ec_lookup_table[ec]
        except KeyError:
            return self.ec_lookup_table[const.TOKEN_DEFAULT]

    def process_a_single_event(self, data_tuple):
        raise NotImplementedError

    def start_processing(self):
        """
        Must return if self.finished is True.
        """
        raise NotImplementedError

    def get_next_data(self):
        """
        get event from input stream.
        """
        data = self._input_stream.get()

        # end of file is reached
        if data[0] is const.TOKEN_END_OF_STREAM:
            self.send_data(data)
            self.finished = True
            return None
        else:
            return data

    def send_data(self, data):
        """
        send data to output stream.
        :param data:
        """
        self._output_stream.put(data)
