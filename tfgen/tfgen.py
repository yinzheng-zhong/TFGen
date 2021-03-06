import pandas as pd
from tfgen.methods.classic import Classic
from tfgen.methods.classic_large_sparse import ClassicLargeSparse
from threading import Thread
import tfgen.const as const
import queue


class TFGen:
    METHOD_CLASSIC = 101
    METHOD_CLASSIC_LARGE_SPARSE = 102

    def __init__(self, observable_event_classes: list, window_size=500, method=METHOD_CLASSIC):
        """
        :param observable_event_classes: list of observable event classes. Use observe_event_classes to get the list if
        it's not available.
        :param window_size: The sliding window size.
        :param method:
        """

        self.ec_lookup = {ec: i for i, ec in enumerate(observable_event_classes)}

        # add predefined event classes
        self.ec_lookup[const.TOKEN_START_OF_TRACE] = len(self.ec_lookup)
        self.ec_lookup[const.TOKEN_END_OF_TRACE] = len(self.ec_lookup)
        self.ec_lookup[const.TOKEN_DEFAULT] = len(self.ec_lookup)

        self.window_size = window_size
        self.input_stream = queue.Queue(maxsize=10)
        self.output_stream = queue.Queue(maxsize=10)

        self.method = method

        self._method_thread = Thread(target=self._select_method().start_processing)
        self._method_thread.start()

        self.input_method = 0

    def _select_method(self, ):
        if self.method == TFGen.METHOD_CLASSIC:
            return Classic(self.ec_lookup, self.window_size, self.input_stream, self.output_stream)
        elif self.method == TFGen.METHOD_CLASSIC_LARGE_SPARSE:
            return ClassicLargeSparse(self.ec_lookup, self.window_size, self.input_stream, self.output_stream)
        else:
            raise Exception("Method not supported")

    def reset(self):
        """
        Reset if new dataset is loaded.
        :return:
        """
        self._method_thread = Thread(target=self._select_method().start_processing)
        self._method_thread.start()

    def stream_termination_signal(self):
        self.input_stream.put((const.TOKEN_END_OF_STREAM, None))

    def _load_from_dataframe_thread(self, event_log, case_id_col, attributes_cols):
        case_ids = event_log[case_id_col].values
        attributes = event_log[attributes_cols].values

        # _ = [self._input_stream.put(sample) for sample in samples]
        # _ = list(map(self._input_stream.put, samples))
        for i in range(len(case_ids)):
            self.input_stream.put((case_ids[i], attributes[i]))

        # make finished signal
        self.stream_termination_signal()

    def load_from_dataframe(self, event_log: pd.DataFrame, case_id_col, attributes_cols):
        """
        Loads data from pandas dataframe. An offline process
        :param event_log: pandas dataframe
        :param case_id_col: the column name
        :param attributes_cols: array of column names
        """
        self.input_method = 0
        Thread(target=self._load_from_dataframe_thread, args=(event_log, case_id_col, attributes_cols)).start()

    def _load_from_generator_thread(self, generator):
        """
        Todo: may need to put end of stream token at the end of the stream.
        :param generator:
        :return:
        """
        # put all data from the generator to the queue
        for sample in generator():
            self.input_stream.put(sample)

    def load_from_generator(self, generator):
        """
        Loads data from generator. Each yield is a tuple of (case_id, attributes), where attributes value is an iterable
        of strings (attribute_1, attribute_2, ...)
        """
        self.input_method = 1
        Thread(target=self._load_from_generator_thread, args=(generator,)).start()

    def load_next(self, case_id, attributes):
        """
        Load stream data one by one.
        :param case_id: str or int
        :param attributes: str. Iterable of attributes (attribute_1, attribute_2, ...).
        """
        self.input_method = 2
        self.input_stream.put((case_id, attributes))

    def get_output_generator(self):
        if self.input_method == 2:
            raise Exception("Cannot get generator with load_next() input."
                            "Use load_from_generator() or load_from_dataframe()")

        while True:
            data = self.output_stream.get()
            if data[0] is const.TOKEN_END_OF_STREAM:
                self.reset()
                return

            yield data

    def get_output_next(self):
        try:
            data = self.output_stream.get(block=False)
        except queue.Empty:
            raise InitialisingException()

        if data[0] is const.TOKEN_END_OF_STREAM:
            self.reset()
            raise StopIteration
        else:
            return data

    def get_output_list(self):
        """
        Returns a list of output samples.
        :return: list of (case_id, features)
        """

        if self.input_method != 0:
            raise Exception("Cannot get offline output in online mode. Use get_output_generator() or "
                            "get_output_next() instead.")

        return list(self.get_output_generator())


class InitialisingException(Exception):
    def __init__(self):
        msg = "TFGen is still initialising (number of input is less than the window size) or preparing the data" \
              ", so there is no output yet."
        super().__init__(msg)
