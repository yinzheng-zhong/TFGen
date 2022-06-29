from methods.base_method import BaseMethod


class Classic(BaseMethod):
    def __init__(self, window_size: int, input_stream, output_stream):
        super().__init__(window_size, input_stream, output_stream)

    def init(self):
        pass

    def start_processing(self):
        self.init()
        pass