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

First we need to get the observable event classes. Better save this for future use, as the change of the event classes
or the change of the order of event classes will change the generated feature. The parameter will be an array or
a list of attributes. Check release `v0.2.1 <https://github.com/yinzheng-zhong/TFGen/releases/tag/v0.2.1>`_ for
datasets we will use below.

.. code-block:: python

    from tfgen.observe_event_classes import get_observable_ec

    data_for_ec = pd.read_csv('test_data_for_ec.csv')
    ec = get_observable_ec(data_for_ec[['Flags', 'S/C']])  # Flags and S/C are the attributes

Now we can create the TFGen object. The first parameter is the list of all possible event classes.
The second parameter is the window size.

.. code-block:: python

    from tfgen import TFGen
    tfgen = TFGen(ec, window_size=500)

Now we load the data for feature generation. Make sure the data are already in chronological order.
Each case needs to end with EOT marking, and it needs to generate
be placed under each attribute. Without EOT, the TET will keep growing. Something like this:

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

We can load the dataset in an offline mode, or we can load the dataset in an online streaming mode.
The method for loading the dataset in offline mode is:

.. code-block:: python

    tfgen.load_from_dataframe(data_for_feature, case_id_col='Case_ID', attributes_cols=['Flags', 'S/C'])
    output = tfgen.get_output_list()  # this will return a list of data.

Note that the output is a list (or other iterable) of tuples (case_id, transition_table),
case_id is from the last event and it can be used for labelling the data for supervised learning.
get_output_list() can only be used in offline mode.

Use the generator as an input for the online streaming.

.. code-block:: python

    # replace this generator with your own generator
    def replace_with_the_actual_generator():
        while True:
            for rows in data_for_feature.values:
                case_id = rows[0]
                event_attrs = rows[[2, 3]]

                yield case_id, event_attrs  # event_attr is an iterable with multiple attributes.

    # Use the generator as an input for the online streaming.
    tfgen.load_from_generator(replace_with_the_actual_generator)
    out = tfgen.get_output_generator()  # this will return a generator as the output.

get_output_generator() can only be used with load_from_dataframe() or load_from_generator().

We can feed the data into TFGen one by one. Note that the output is not guaranteed as TFGen needs several events to
initialise. Handel the exception if you want to use this method.

.. code-block:: python

    import queue
    data_for_feature_array = data_for_feature.values
    for sample in data_for_feature_array:
        case_id = sample[0]
        event_attrs = sample[[2, 3]]

        # tfgen.load_next(<you data sample>). The sample is a tuple of (case_id, event_attrs)
        # and event_attrs is an iterable with multiple attributes.
        tfgen.load_next(case_id, event_attrs)
        try:
            print(tfgen.get_output_next())
        except InitialisingException:
            continue

get_output_next() is compatible with all input methods.
