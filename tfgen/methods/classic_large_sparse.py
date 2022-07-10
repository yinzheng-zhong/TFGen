from classic import Classic
from scipy.sparse import csr_matrix


class ClassicLargeSparse(Classic):
    def __init__(self, ec_lookup_table, window_size, input_stream, output_stream):
        """
        Classic method suitable for large event class space
        """
        super().__init__(ec_lookup_table, window_size, input_stream, output_stream)

    def make_data_avail(self):
        self.send_data((self.current_case, csr_matrix(self.transition_counts)))
