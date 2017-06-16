# Adapted from: https://github.com/stevenwei/chargify-python
import requests


class ChargifyError(Exception):
    pass


class ChargifyConnectionError(ChargifyError):
    pass


class ChargifyUnauthorizedError(ChargifyError):
    pass


class ChargifyForbiddenError(ChargifyError):
    pass


class ChargifyNotFoundError(ChargifyError):
    pass


class ChargifyUnprocessableEntityError(ChargifyError):
    pass


class ChargifyServerError(ChargifyError):
    pass


# Maps certain function names to HTTP verbs
VERBS = {
    'create': 'POST',
    'read': 'GET',
    'update': 'PUT',
    'delete': 'DELETE',
}

# A list of identifiers that should be extracted and placed into the url string if they are
# passed into the kwargs.
IDENTIFIERS = {
    'customer_id': 'customers',
    'product_id': 'products',
    'subscription_id': 'subscriptions',
    'component_id': 'components',
    'handle': 'handle',
}

# Valid response formats
VALID_FORMATS = ['json', 'xml']


class ChargifyHttpClient(object):
    """
    Extracted from the main Chargify class so it can be stubbed out during testing.
    """

    def make_request(self, method, url, params, data, api_key):
        """
        Actually responsible for making the HTTP request.
        :param url: The URL to load.
        :param method: The HTTP method to use.
        :param data: Any POST data that should be included with the request.
        """
        result = requests.request(method, url, params=params, json=data, auth=(api_key, 'X'))

        if result.ok:
            if 'json' in result.headers.get('content-type'):
                return result.json(), result.status_code
            return result.text, result.status_code

        if result.status_code == 401:
            raise ChargifyUnauthorizedError()
        elif result.status_code == 403:
            raise ChargifyForbiddenError()
        elif result.status_code == 404:
            raise ChargifyNotFoundError()
        elif result.status_code == 422:
            raise ChargifyUnprocessableEntityError()
        elif result.status_code == 500:
            raise ChargifyServerError()
        else:
            raise ChargifyError()


class Chargify(object):
    """
    A client for the Chargify API.
    """
    api_key = ''
    sub_domain = ''
    path = []
    domain = 'https://%s.chargify.com/'
    client = None
    format = None

    def __init__(self, api_key, sub_domain, path=None, client=None, format=None):
        """
        :param api_key: The API key for your Chargify account.
        :param sub_domain: The sub domain of your Chargify account.
        :param path: The current path constructed for this request.
        :param client: The HTTP client to use to make the request.
        :param format: The desire response format for the request.
        """
        if format:
            msg = 'Format must be one of: ' + ', '.join(VALID_FORMATS)
            assert format.lower() in VALID_FORMATS, msg
        self.api_key = api_key
        self.sub_domain = sub_domain
        self.path = path or []
        self.client = client or ChargifyHttpClient()
        self.format = format or 'json'

    def __getattr__(self, attr):
        """
        Uses attribute chaining to help construct the url path of the request.
        """
        try:
            return object.__getattr__(self, attr)
        except AttributeError:
            return Chargify(self.api_key, self.sub_domain, self.path + [attr], self.client,
                            format=self.format)

    def construct_request(self, **kwargs):
        """
        :param kwargs: The arguments passed into the request. Valid values are:
            'customer_id', 'product_id', 'subscription_id', 'component_id', 'handle' will be
            extracted and placed into the url. 'data' will be serialized into a JSON string and
            POSTed with the request.
        """
        path = self.path[:]

        # Find the HTTP method if we were called with create(), update(), read(), or delete()
        if path[-1] in VERBS.keys():
            action = path.pop()
            method = VERBS[action]
        else:
            method = 'GET'

        # Extract certain kwargs and place them in the url instead
        for identifier, name in IDENTIFIERS.items():
            value = kwargs.pop(identifier, None)
            if value:
                path.append(str(value))

        # Convert the data to a JSON string
        data = kwargs.pop('data', {})

        # Build url
        url = self.domain % self.sub_domain
        url = url + '/'.join(path) + '.' + self.format.lower()

        return method, url, kwargs, data

    def __call__(self, **kwargs):
        method, url, params, data = self.construct_request(**kwargs)
        return self.client.make_request(method, url, params, data, self.api_key)
