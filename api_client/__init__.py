import json
import os
from urllib.parse import urlsplit, urlunsplit

import requests


class BaseAPIClient(object):
    """ Base class for API clients implementation
    """
    force_trailing_backslash = True

    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
        }
        self.auth = None


    def prepare_url(self, path):
        parts = urlsplit(self.get_endpoint())
        
        if self.force_trailing_backslash and path[-1] != "/":
            path += "/"

        return urlunsplit((
            parts.scheme, parts.netloc,
            os.path.join(parts.path, path),
            "", ""))


    def _make_request(self, url, method, headers, data, **kwargs):
        auth = self.auth or None

        if method == "POST":
            response = requests.post(
                url, data=data, headers=headers, auth=auth, **kwargs)
        elif method == "PUT":
            response = requests.put(
                url, data=data, headers=headers, auth=auth, **kwargs)
        elif method == "DELETE":
            response = requests.delete(
                url, data=data, headers=headers, auth=auth, **kwargs)
        else:
            response = requests.get(
                url, headers=headers, params=data, auth=auth, **kwargs)

        return response


    def _make_requests(
            self, path, method="GET", data=None, extra_headers=None,
            retry_count=1, **kwargs):

        headers = self.prepare_headers(extra_headers=extra_headers)
        data = self.prepare_data(data, method)

        url = self.prepare_url(path)

        try_count = 1 + (0 if not retry_count else retry_count)

        while try_count > 0:
            try_count -= 1
            response = self._make_request(
                url, method, headers, data, **kwargs)

            if not self.should_retry(response, try_count):
                break

        return self.process_response(response)


    def prepare_headers(self, extra_headers=None):
        headers = {}
        headers.update(self.headers)
        if extra_headers:
            headers.update(extra_headers)

        return headers


    def prepare_data(self, data, method="POST"):
        if data is not None:
            if method in ["POST", "PUT"]:
                return json.dumps(data)

        return data


    def should_retry(self, response, retries_left):
        return False


    def get_endpoint(self):
        """
        Returns API endpoint, a full URL
        """
        raise NotImplementedError(
            "You must create a subclass of APIClient to use it")


    def post(
            self, url, data=None, extra_headers=None, retry_count=1,
            **kwargs):
        response = self._make_requests(
            url, method='POST', data=data, extra_headers=extra_headers,
            retry_count=retry_count, **kwargs)
        return response


    def put(
            self, url, data=None, extra_headers=None, retry_count=1,
            **kwargs):
        response = self._make_requests(
            url, method='PUT', data=data, extra_headers=extra_headers,
            retry_count=retry_count, **kwargs)
        return response


    def get(
            self, url, data=None, extra_headers=None, retry_count=1,
            **kwargs):
        response = self._make_requests(
            url, method='GET', data=data, extra_headers=extra_headers,
            retry_count=retry_count, **kwargs)
        return response


    def delete(
            self, url, data=None, extra_headers=None, retry_count=1,
            **kwargs):
        response = self._make_requests(
            url, method='DELETE', data=data, extra_headers=extra_headers,
            retry_count=retry_count, **kwargs)
        return response


    def process_response(self, response):
        response.raise_for_status()

        return response
