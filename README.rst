Transition-based Feature Generator (TFGen)
==========================================

.. image:: https://img.shields.io/pypi/v/tfgen.svg?color=brightgreen
   :target: https://pypi.org/project/tfgen/
   :alt: PyPI version

Description
^^^^^^^^^^^

The process log/event log will be used as input for the feature generator. The feature generator will generate transition matrices.

How to use
^^^^^^^^^^

**Installation**

.. code-block:: bash

    pip install tfgen    # normal install
    pip install --upgrade tfgen  # update tfgen

**How to use**

The observable event classes are first required, and they can be acquired using the method "get observable ec()".
The generated features will change if the event classes or the order of the event classes are changed, so it is
preferable to save the observable event classes for later use. A dataframe/list/array of attributes should be the
method's first parameter. The datasets we'll use for the following code examples are available in release
`v0.2.1 <https://github.com/yinzheng-zhong/TFGen/releases/tag/v0.2.1>`_ on Github.

.. code-block:: python

    from tfgen.observe_event_classes import get_observable_ec

    data_for_ec = pd.read_csv('test_data_for_ec.csv')
    ec = get_observable_ec(data_for_ec[['Flags', 'S/C']])  # Flags and S/C are the attributes

We can now start creating the TFGen object. A list of observable event classes that we obtained in the previous step is
the first parameter. The window size is the second variable.

.. code-block:: python

    from tfgen import TFGen
    tfgen = TFGen(ec, window_size=500)

We are currently loading the event log data to create features. Before sending the data to TFGen, make sure it is
already in chronological order. EOT marking is required at the ending of each case, and it must be done under each
attribute. Without EOT, the TET will continue to expand. Possibly like this:

.. list-table:: Example of input data.
   :widths: 25 25 25
   :header-rows: 1

   * - Case_ID
     - Flags
     - S/C
   * - ...
     - ...
     - ...
   * - 13
     - 000.ACK.FIN.
     - C
   * - 13
     - 000.ACK.
     - S
   * - 14
     - 000.SYN.
     - C
   * - 13
     - 000.ACK.RST.
     - S
   * - 13
     - EOT
     - EOT
   * - 14
     - 000.ACK.SYN.
     - S
   * - ...
     - ...
     - ...

.. code-block:: python

    data_for_feature = pd.read_csv('test_data_with_eot.csv')

We can load the offline dataset or load the dataset in an online streaming mode. The method for loading the dataset
in offline mode is:

.. code-block:: python

    tfgen.load_from_dataframe(data_for_feature, case_id_col='Case_ID', attributes_cols=['Flags', 'S/C'])
    output = tfgen.get_output_list()  # this will return a list of data.

Note that the output is a list (or other iterable) of tuples where each tuple contains two variables
(case_id, transition_table). The case_id comes from the last processed event, and it can be used for labelling the data
for supervised learning or validation. "get_output_list()" can only be used in offline mode.

The following example uses the generator as input for online streaming mode.

.. code-block:: python

    # replace this generator with the actual generator
    def replace_with_the_actual_generator():
        while True:
            for rows in data_for_feature.values:
                case_id = rows[0]
                event_attrs = rows[[2, 3]]

                yield case_id, event_attrs  # event_attr is an iterable with multiple attributes.

    # Use the generator as an input for online streaming.
    tfgen.load_from_generator(replace_with_the_actual_generator)
    out = tfgen.get_output_generator()  # this will return a generator as the output.

Only the input methods "load_from_dataframe()" or "load_from_generator()" can be used with the output method
"get_output_generator()".

The data can be entered one at a time into TFGen. Due to the fact that TFGen requires several events to initialise,
the output is not guaranteed. To use this method, handle the InitialisingException exception.

.. code-block:: python

    from tfgen import InitialisingException

    data_for_feature_array = data_for_feature.values
    for sample in data_for_feature_array:
        case_id = sample[0]
        event_attrs = sample[[2, 3]]

        # tfgen.load_next(<your data sample>). The sample is a tuple of (case_id, event_attrs)
        # and event_attrs is an iterable with multiple attributes.
        tfgen.load_next(case_id, event_attrs)
        try:
            print(tfgen.get_output_next())
        except InitialisingException:
            continue

The output method "get_output_next()" is compatible with all input methods.

Methods
^^^^^^^

Currently, the "Classic" and the "ClassicLargeSparse" methods for feature generation are available. The "Classic"method
is employed by default. The "ClassicLargeSparse" method can be used to output Scipy sparse matrices for event logs that
contain a larger number of event classes.

.. code-block:: python

        from tfgen import TFGen

        tfgen = TFGen(ec, window_size=500, method=TFGen.ClassicLargeSparse)

Implementing New Methods
^^^^^^^^^^^^^^^^^^^^^^^
By deriving from the "BaseMethod" located in "tfgen/methods/base method.py," one can extend the existing methods by
creating new method classes. All classes must be placed under "tfgen/methods/" directory. The next event sample must
be obtained using method "self.get_next_data()," and the generated feature must be sent to the output using
method "self.send_data()".
"self.finished" will become "True" if the input stream reaches the end.

.. code-block:: python

    from tfgen.methods.base_method import BaseMethod

    class NewMethod(BaseMethod):
    def __init__(self, ec_lookup_table, window_size, input_stream, output_stream):
        super().__init__(ec_lookup_table, window_size, input_stream, output_stream)

    # entry
    def start_processing(self):
        while True:
            # event is a tuple of (case_id, event_attrs)
            event = self.get_next_data()
            # do something
            self.send_data(processed_data)
            if self.finished:
                break
Then include the new method in the "TFGen" class found in "tfgen/tfgen.py". Two locations are required to be modified.

.. code-block:: python
    class TFGen:
        METHOD_CLASSIC = 101
        METHOD_CLASSIC_LARGE_SPARSE = 102
        METHOD_NEW_METHOD = 103  # The first location. New method class

        def _select_method(self, method):
        if method == TFGen.METHOD_CLASSIC:
            return Classic(self.ec_lookup, self.window_size, self.input_stream, self.output_stream)
        elif method == TFGen.METHOD_CLASSIC_LARGE_SPARSE:
            return ClassicLargeSparse(self.ec_lookup, self.window_size, self.input_stream, self.output_stream)
        # The second location. The instance to the new method class
        elif method == TFGen.METHOD_NEW_METHOD:
            return NewMethod(self.ec_lookup, self.window_size, self.input_stream, self.output_stream)
        else:
            raise Exception("Method not supported")
