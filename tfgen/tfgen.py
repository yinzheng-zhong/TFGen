import pandas as pd
import numpy as np
from methods.classic import Classic
from threading import Thread
import const
import queue

METHOD_CLASSIC = 101


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
        self.ec_lookup[const.TOKEN_END_OF_TRACE] = len(self.ec_lookup)
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

    def load_from_dataframe(self, event_log: pd.DataFrame, case_id_col: str, attributes_cols: list):
        """
        Loads data from pandas dataframe. An offline process
        :param event_log: pandas dataframe
        :param case_id_col: the column name
        :param attributes_cols: array of column names
        """
        self.realtime = False

        case_ids = event_log[case_id_col].values
        attributes = event_log[attributes_cols].astype(str).values
        """convert attributes to string"""

        samples = zip(case_ids, attributes)

        map(self.input_stream.put, samples)
        self._method_thread.join()

    def load_from_generator(self, generator):
        """
        Loads data from generator. Each yield is a tuple of (case_id, attributes), where attributes value is a tuple of
        strings (attribute_1, attribute_2, ...)
        """
        self.realtime = True
        map(self.input_stream.put, generator)

    def load_next(self, case_id, *attributes):
        """
        Load stream data one by one.
        :param case_id: str or int
        :param attributes: str. Tuple of attributes (attribute_1, attribute_2, ...).
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
        return next(self.get_output_generator())

    def get_output_ndarray(self):
        if self.realtime:
            raise Exception("Cannot get ndarray output in realtime mode. Use get_output_generator() or "
                            "get_output_next() instead")

        return np.array(list(self.get_output_generator()))

