Welcome to sponsorblock.py's documentation!
===========================================

.. meta::
   :description: Documentation for sponsorblock.py
   :keywords: sponsorblock.py, documentation, sponsorblock, python, wrapper
   :author: Wasi Master


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api_reference


sponsorblock.py is a easy to use, fast, and powerful wrapper around the sponsorblock api

Example of getting the segments of a video using sponsorblock.py

>>> import sponsorblock as sb
>>> client = sb.Client()
>>> segments = client.get_skip_segments("https://www.youtube.com/watch?v=kJQP7kiw5Fk")
>>> segments
[
   Segment(category=music_offtopic, start=0, end=21.808434, uuid=728cbf1743f4b5230ee4a9c7b254e316aa90720ec35297b17aaf6d23907c1a83, duration=0:00:21.808434, action_type=skip),
   Segment(category=music_offtopic, start=249.6543, end=281.521, uuid=ae38abe70c63b093eaeb1c2c437aa3275856646c326ee23b5ff70dcb4190c92f, duration=0:00:31.866700, action_type=skip),
   Segment(category=outro, start=274.674, end=281.521, uuid=cd335e7f406df63e460b4b02db71cc57344529d381bb9fc482960f338ff4ae37, duration=0:00:06.847000, action_type=skip)
]
>>> segments[0].category
'music_offtopic'
>>> segments[1].start, segments[1].end
(249.6543, 281.521)
>>> segments[2].duration.seconds
6

For more information, see :ref:`API Reference <api_reference>`

There is also a cli that you can use to get segments from the command line (beta).
To use that run `sponsorblock video_id` and pass your desired video_id

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`api_reference`
* :ref:`search`
