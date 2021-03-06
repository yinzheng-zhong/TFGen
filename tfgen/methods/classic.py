from abc import ABC

from tfgen.methods.base_method import BaseMethod
import tfgen.utils as utils
from time import time
from tfgen import const
import numpy as np


class Classic(BaseMethod, ABC):
    def __init__(self, ec_lookup_table, window_size, input_stream, output_stream):
        super().__init__(ec_lookup_table, window_size, input_stream, output_stream)

        # 10% performance increase by increase/decrease the transition_matrix by a small step (1/window size)
        # instead of normalise like transition_count/window size. Saved a division operation.
        self.step = 1 / window_size

    def init_window(self):
        for _ in range(self.window_size):
            event = self.get_next_data()

            if self.finished:
                return

            self.process_a_single_event(event)

        self.make_data_avail()

    def make_data_avail(self):
        self.send_data((self.current_case, np.array(self.transition_counts)))

    def process_a_single_event(self, data_tuple):
        case_id, event_attr = data_tuple

        if all(map(lambda x: x == const.TOKEN_END_OF_TRACE, event_attr)):
            event_class = const.TOKEN_END_OF_TRACE
        else:
            event_class = utils.convert_attr_to_ec(event_attr)

        prev = self.tet.update_event(case_id, event_class)

        # reduce the count for transition that went outside the window.
        if len(self.sliding_window_buffer) >= self.window_size:
            transition_out_window = self.sliding_window_buffer[0]
            self.transition_counts[transition_out_window] -= self.step

        # add the count for the transition that come in.
        transition_new = (self.index_lookup(prev), self.index_lookup(event_class))
        self.sliding_window_buffer.append(transition_new)
        self.transition_counts[transition_new] += self.step

        self.current_case = case_id

    def start_processing(self):
        self.init_window()

        if self.finished:
            return

        count = 0

        last_benchmark = time()

        while True:
            event = self.get_next_data()

            if self.finished:
                return

            self.process_a_single_event(event)
            count += 1

            if not count % 100000:
                now = time()
                print('Processing speed: {} events/s. TET size: {}'.format(
                    100000 / (now - last_benchmark),
                    len(self.tet.table)
                ))
                last_benchmark = now
                count = 0

            self.make_data_avail()
