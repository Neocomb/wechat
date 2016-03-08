import hashlib
import time
import requests
from lxml import etree
from .webapp import app
from flask import json

DEFAULT_ENCODING = 'utf-8'
WECHAT_TOKEN = ''


class WXError(Exception):
    pass


class WXAPIError(WXError):
    def __init__(self, errcode, errmsg):
        self.errcode = errcode
        self.errmsg = errmsg

    def __str__(self):
        return 'WXApiError({}): {}'.format(self.errcode, self.errmsg)


API_URL_DESCS = {
    'grant_client_credential': {
        'method': 'GET',
        'content_type': 'json',
        'url': 'https://api.weixin.qq.com/cgi-bin/token',
    },
    'create_menu': {
        'method': 'POST',
        'content_type': 'json',
        'url': 'https://api.weixin.qq.com/cgi-bin/menu/create',
    },
    'media_upload_img': {
        'method': 'POST',
        'content_type': 'json',
        'url': 'https://api.weixin.qq.com/cgi-bin/media/uploadimg',
    },
    'media_upload_news': {
        'method': 'POST',
        'content_type': 'json',
        'url': 'https://api.weixin.qq.com/cgi-bin/media/uploadnews',
    },
    'add_material': {
        'method': 'POST',
        'content_type': 'json',
        'url': 'https://api.weixin.qq.com/cgi-bin/material/add_material',
    },
    'add_material_news': {
        'method': 'POST',
        'content_type': 'json',
        'url': 'https://api.weixin.qq.com/cgi-bin/material/add_news',
    },
    'get_material': {
        'method': 'POST',
        'content_type': 'json',
        'url': 'https://api.weixin.qq.com/cgi-bin/material/get_material',
    },
    'msg_sendall': {
        'method': 'POST',
        'content_type': 'json',
        'url': 'https://api.weixin.qq.com/cgi-bin/message/mass/sendall',
    },
    'get_ticket': {
        'method': 'GET',
        'content_type': 'json',
        'url': 'https://api.weixin.qq.com/cgi-bin/ticket/getticket'
    },
    'get_user': {
        'method': 'GET',
        'content_type': 'json',
        'url': 'https://api.weixin.qq.com/cgi-bin/user/info'
    }
}


def validate_message(request):
    signature1 = request.args['signature']
    timestamp = request.args['timestamp']
    nonce = request.args['nonce']

    raw_signature = ''.join(sorted([app.config['WX_TOKEN'], timestamp, nonce])).encode('ascii')
    signature2 = hashlib.sha1(raw_signature).hexdigest()
    if signature1 != signature2:
        raise WXError('could not validate message origin')


def xml_string_to_dict(string):
    xml_root = etree.fromstring(string)

    def xml_node_to_dict(xml_node, dict_node):
        for child in xml_node:
            if child.text:
                new_node = child.text
            else:
                new_node = {}
                xml_node_to_dict(child, new_node)

            if child.tag in dict_node:
                # handle array
                if not isinstance(dict_node[child.tag], (list, tuple)):
                    dict_node[child.tag] = [dict_node[child.tag]]
                dict_node[child.tag].append(new_node)
            else:
                dict_node[child.tag] = new_node

    dict_root = {}
    xml_node_to_dict(xml_root, dict_root)
    return dict_root


def dict_to_xml_string(dict_):
    xml_root = etree.Element('xml')

    def dict_to_xml_node(dict_node, xml_node):
        for key, value in sorted(dict_node.items()):
            import abc
            if isinstance(value, abc.Mapping):
                ele = etree.SubElement(xml_node, key)
                dict_to_xml_node(value, ele)
            elif isinstance(value, (list, tuple)):
                for subvalue in value:
                    ele = etree.SubElement(xml_node, key)
                    dict_to_xml_node(subvalue, ele)
            else:
                ele = etree.SubElement(xml_node, key)
                ele.text = etree.CDATA(str(value))

    dict_to_xml_node(dict_, xml_root)
    return etree.tostring(xml_root, encoding=DEFAULT_ENCODING)


def make_base_reply_message_from_message(req):
    return {
        'ToUserName': req['FromUserName'],
        'FromUserName': req['ToUserName'],
        'CreateTime': int(time.time()),
    }


def do_request(api_name, query_params=None, data=None, json_data=None, files=None,
               need_access_token=True):
    api_url_desc = API_URL_DESCS[api_name]
    url = api_url_desc['url']
    if need_access_token:
        if not query_params:
            query_params = {'access_token': WECHAT_TOKEN}
        else:
            if 'access_token' not in query_params:
                query_params['access_token'] = WECHAT_TOKEN
    headers = {}
    if json_data is not None:
        assert not data
        data = json.dumps(json_data, ensure_ascii=False, encoding=DEFAULT_ENCODING)
        headers['Content-Type'] = 'application/json'
    app.logger.debug("requesting wechat api %(api_name)s with params: %(params)s and data %(data)s",
                     {'api_name': api_name, 'params': query_params, 'data': data})

    response = getattr(requests, api_url_desc['method'].lower())(url, params=query_params,
                                                                 data=data, headers=headers,
                                                                 files=files,
                                                                 timeout=5.0)
    app.logger.debug("response from wechat of api %(api_name)s with content %(content)s",
                     {'api_name': api_name, 'content': response.content})
    if api_url_desc['content_type'] == 'json':
        json_content = response.json()
        if json_content.get('errcode', 0) != 0:
            raise WXAPIError(json_content['errcode'], json_content['errmsg'])
        return response.json(), response
    else:
        return response.content, response


def refresh_access_token():
    params = {
        'grant_type': 'client_credential',
        'appid': app.config['WX_APPID'],
        'secret': app.config['WX_APP_SECRET']
    }
    ret, _ = do_request('grant_client_credential', params, need_access_token=False)
    WECHAT_TOKEN = ret['access_token']
    return ret['access_token']
