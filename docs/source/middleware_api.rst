Middleware API
==============
The middleware consist of communcation classes that can be used to communicate to the backend.
Each class inherits the API sturcture from the `stacking_backend.middleware.base_connector.BaseConnector` class.
All methods that raise a `NotImplementedError` must be implemented in the child class.

.. autosummary::
    :toctree: generated

    stacking_middleware.base_connector.BaseConnector