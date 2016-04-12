#!/usr/bin/env python
# encoding: utf-8

class WXError(Exception):
    pass


def validate_message(request):
    signature1 = request.args['signature']
    timestamp = request.args['timestamp']
    nonce = request.args['nonce']

    raw_signature = ''.join(sorted([app.config['WX_TOKEN'], timestamp, nonce])).encode('ascii')
    signature2 = hashlib.sha1(raw_signature).hexdigest()
    if signature1 != signature2:
        raise WXError('could not validate message origin')
