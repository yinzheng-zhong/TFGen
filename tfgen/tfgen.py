import pandas as pd
from tfgen.methods.classic import Classic
from threading import Thread
import tfgen.const as const
import queue

METHOD_CLASSIC = const.METHOD_CLASSIC


class TFGen:
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

        self._method_thread = Thread(target=self._select_method(method).start_processing)
        self._method_thread.start()

        self.realtime = True

    def _select_method(self, method):
        if method == METHOD_CLASSIC:
            return Classic(self.ec_lookup, self.window_size, self.input_stream, self.output_stream)
        else:
            raise Exception("Method not supported")

    def _load_from_dataframe_thread(self, event_log, case_id_col, attributes_cols):
        case_ids = event_log[case_id_col].values
        attributes = event_log[attributes_cols].astype(str).values
        """convert attributes to string"""

        samples = zip(case_ids, attributes)

        # _ = [self.input_stream.put(sample) for sample in samples]
        # _ = list(map(self.input_stream.put, samples))
        for sample in samples:
            self.input_stream.put(sample)

    def load_from_dataframe(self, event_log: pd.DataFrame, case_id_col: str, attributes_cols: list):
        """
        Loads data from pandas dataframe. An offline process
        :param event_log: pandas dataframe
        :param case_id_col: the column name
        :param attributes_cols: array of column names
        """
        self.realtime = False
        Thread(target=self._load_from_dataframe_thread, args=(event_log, case_id_col, attributes_cols)).start()

    def _load_from_generator_thread(self, generator):
        # put all data from the generator to the queue
        for sample in generator():
            self.input_stream.put(sample)

    def load_from_generator(self, generator):
        """
        Loads data from generator. Each yield is a tuple of (case_id, attributes), where attributes value is an iterable
        of strings (attribute_1, attribute_2, ...)
        """
        self.realtime = True
        Thread(target=self._load_from_generator_thread, args=(generator,)).start()

    def load_next(self, case_id, *attributes):
        """
        Load stream data one by one.
        :param case_id: str or int
        :param attributes: str. Iterable of attributes (attribute_1, attribute_2, ...).
        """
        self.realtime = True
        self.input_stream.put((case_id, attributes))

    def get_output_generator(self):
        while True:
            try:
                yield self.output_stream.get(block=True, timeout=1)
            except queue.Empty:
                if not self.realtime:
                    break

    def get_output_next(self):
        generator = self.get_output_generator()
        return next(generator)

    def get_output_list(self):
        if self.realtime:
            raise Exception("Cannot get ndarray output in realtime mode. Use get_output_generator() or "
                            "get_output_next() instead")

        return list(self.get_output_generator())

