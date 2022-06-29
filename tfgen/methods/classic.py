from abc import ABC

from tfgen.methods.base_method import BaseMethod
import tfgen.utils as utils


class Classic(BaseMethod, ABC):
    def __init__(self, ec_lookup_table, window_size, input_stream, output_stream):
        super().__init__(ec_lookup_table, window_size, input_stream, output_stream)

    def init_window(self):
        for _ in range(self.window_size):
            self.process_a_single_event()

        self.output_stream.put(
            {'case_id': self.current_case, 'transition_table': self.transition_counts / self.window_size}
        )

    def process_a_single_event(self):
        case_id, event_attr = self.input_stream.get()
        event_class = utils.convert_attr_to_ec(event_attr)
        prev = self.tet.update_event(case_id, event_class)

        row = self.index_lookup(prev)
        column = self.index_lookup(event_class)

        self.transition_counts[row, column] += 1
        self.current_case = case_id

    def start_processing(self):
        self.init_window()

        while True:
            self.process_a_single_event()

            self.output_stream.put(
                {'case_id': self.current_case, 'transition_table': self.transition_counts / self.window_size}
            )
