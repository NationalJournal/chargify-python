import requests

class ChargifyError(Exception):
    """
    Base Charfigy error exception.
    """
    def __init__(self, status_code=None, error_data=None, *args, **kwargs):
        super(ChargifyError, self).__init__(*args, **kwargs)
        self.status_code = status_code
        self.error_data = error_data or {}


class ChargifyConnectionError(ChargifyError):
    pass


class ChargifyUnauthorizedError(ChargifyError):
    pass


class ChargifyForbiddenError(ChargifyError):
    pass


class ChargifyNotFoundError(ChargifyError):
    pass


class ChargifyDuplicateSubmissionError(ChargifyError):
    pass


class ChargifyUnprocessableEntityError(ChargifyError):
    pass


class ChargifyServerError(ChargifyError):
    pass


# Map HTTP status codes to exceptions.
STATUS_EXCEPTIONS = {
    401: ChargifyUnauthorizedError,
    403: ChargifyForbiddenError,
    404: ChargifyNotFoundError,
    409: ChargifyDuplicateSubmissionError,
    422: ChargifyUnprocessableEntityError,
    500: ChargifyServerError,
}

# Maps certain function names to HTTP verbs.
VERBS = {
    'create': 'POST',
    'read': 'GET',
    'update': 'PUT',
    'delete': 'DELETE',
}

# A list of identifiers that should be extracted and placed into the url string
# if they are passed into the kwargs.
IDENTIFIERS = {
    'customer_id': 'customers',
    'product_id': 'products',
    'subscription_id': 'subscriptions',
    'component_id': 'components',
    'handle': 'handle',
    'statement_id': 'statements',
    'product_family_id': 'product_families',
    'coupon_id': 'coupons',
    'code_id': 'codes',
    'transaction_id': 'transactions',
    'usage_id': 'usages',
    'migration_id': 'migrations',
    'payment_profile_id': 'payment_profiles',
    'invoice_id': 'invoices',
}

# Valid response formats
VALID_FORMATS = ['json', 'xml']


class ChargifyHttpClient(object):
    """
    Extracted from the main Chargify class so it can be stubbed out during
    testing.
    """
    def make_request(self, url, method, params, data, api_key):
        """
        Actually responsible for making the HTTP request.
        :param url: The URL to load.
        :param method: The HTTP method to use.
        :param data: Any POST data that should be included with the request.
        """
        response = requests.request(method, url, params=params, json=data,
                                    auth=(api_key, 'X'))

        is_json = 'json' in response.headers.get('content-type')
        if response.ok:
            if is_json:
                return response.json()
            return response.text

        try:
            exc_cls = STATUS_EXCEPTIONS[response.status_code]
        except KeyError:
            exc_cls = ChargifyError

        error_data = response.json() if is_json else {'body': response.content}
        raise exc_cls(status_code=response.status_code, error_data=error_data)


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

    def __init__(self, api_key, sub_domain, path=None, client=None,
                 format=None):
        """
        :param api_key: The API key for your Chargify account.
        :param sub_domain: The sub domain of your Chargify account.
        :param path: The current path constructed for this request.
        :param client: The HTTP client to use to make the request.
        :param format: The desired response format for the request.
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
            return Chargify(self.api_key, self.sub_domain, self.path + [attr],
                            self.client, format=self.format)

    def construct_request(self, **kwargs):
        """
        :param kwargs: The arguments passed into the request. Valid values are:
            'customer_id', 'product_id', 'subscription_id', 'component_id',
            'handle' will be extracted and placed into the url. 'data' will be
            serialized into a JSON string and POSTed with the request.
        """
        path = self.path[:]

        # Find the HTTP method if we were called with create(), update(),
        # read(), or delete()
        if path[-1] in VERBS.keys():
            action = path.pop()
            method = VERBS[action]
        else:
            method = 'GET'

        # Extract certain kwargs and place them in the url instead
        for identifier, name in IDENTIFIERS.items():
            value = kwargs.pop(identifier, None)
            if value:
                # Insert the identifier value into the URL immediately
                # after the identifier.
                path.insert(path.index(name) + 1, str(value))

        # Convert the data to a JSON string
        data = kwargs.pop('data', {})

        # Build url
        url = self.domain % self.sub_domain
        url = url + '/'.join(path) + '.' + self.format.lower()

        return url, method, kwargs, data

    def __call__(self, **kwargs):
        url, method, params, data = self.construct_request(**kwargs)
        return self.client.make_request(url, method, params, data,
                                        self.api_key)

class ChargifyClient(object):
    """
    An actual pythonic and EXPLICIT client for the Chargify API.
    """
    api_key = ''
    sub_domain = ''
    domain = 'https://%s.chargify.com'
    client = ChargifyHttpClient()

    def __init__(self, api_key, sub_domain):
        """
        :param api_key: The API key for your Chargify account.
        :param sub_domain: The sub domain of your Chargify account.
        """
        self.api_key = api_key
        self.domain = self.domain % sub_domain

    def get_management_link(self, customer_id):
        """
        endpoint: /portal/customers/{customer_id}/management_link.json
        :param customer_id: get the Chargify Billing Portal Management Link for 
        the given customer id. 
        """
        url = self.domain + f"/portal/customers/{customer_id}/management_link.json"
        return self.client.make_request(url, "GET", None, None, self.api_key)

    def api_request(self, path, method="GET", data=None):
        """
        Arbitrary chargify api request handler.
        :param path: any chargify endpoint url.
        :param method: method type GET, POST, etc
        return: json
        """
        url = self.domain + path
        return self.client.make_request(url, method, None, data, self.api_key)