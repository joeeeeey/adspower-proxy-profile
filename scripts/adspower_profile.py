#!/usr/bin/env python3
"""Preview, create and launch AdsPower profiles with credential-safe proxy input."""
import argparse
import ipaddress
import json
import os
import sys
from urllib.parse import urlsplit,unquote
from safety import SafeError, secret, api_url, request

def parse_proxy(raw):
    p=urlsplit(raw)
    if p.scheme not in ('http','https','socks5') or not p.hostname or not p.port or p.path not in ('','/') or p.query or p.fragment:
        raise SafeError('Proxy URL needs http/https/socks5, host and port; no path/query/fragment.')
    if (p.username is None) != (p.password is None):
        raise SafeError('Supply both proxy username and password, or neither.')
    return {'proxy_soft':'other','proxy_type':p.scheme,'proxy_host':p.hostname,'proxy_port':str(p.port),
            'proxy_user':unquote(p.username or ''),'proxy_password':unquote(p.password or '')}

def local_base(base):
    p=urlsplit(base)
    try:local = p.hostname=='localhost' or ipaddress.ip_address(p.hostname).is_loopback
    except ValueError:local=False
    if p.scheme!='http' or not local or p.username or p.password or p.path not in ('','/') or p.query or p.fragment:
        raise SafeError('AdsPower Local API must use an HTTP loopback origin.')
    return base.rstrip('/')

def call(base,path,method='GET',body=None,params=None):
    headers={}
    if os.environ.get('ADSPOWER_API_KEY') or os.environ.get('ADSPOWER_API_KEY_FILE'):
        headers['Authorization']='Bearer '+secret('ADSPOWER_API_KEY','ADSPOWER_API_KEY_FILE')
    value=request(api_url(local_base(base),path,params),headers=headers,method=method,body=body)[1]
    if value.get('code')!=0:raise SafeError('AdsPower rejected the request; inspect the app. No automatic retry.')
    return value.get('data',{})

def payload(args,proxy):
    p=urlsplit(args.url)
    if p.scheme not in ('https','http') or not p.hostname or p.username or p.password:
        raise SafeError('Default page must be an HTTP(S) URL without credentials.')
    return {'name':args.name,'group_id':args.group_id,'open_urls':[args.url],
            'user_proxy_config':proxy,'fingerprint_config':{'automatic_timezone':'1','webrtc':'disabled'}}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--api-base',default='http://127.0.0.1:50325')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('status')
    c=sub.add_parser('create');c.add_argument('--name',required=True);c.add_argument('--group-id',default='0')
    c.add_argument('--url',default='https://example.com');c.add_argument('--execute',action='store_true')
    for n in ('start','stop'):
        q=sub.add_parser(n);q.add_argument('profile_id');q.add_argument('--execute',action='store_true')
    a=p.parse_args(argv)
    try:
        local_base(a.api_base)
        if a.command=='status':out=call(a.api_base,'/status')
        elif a.command=='create':
            proxy=parse_proxy(secret('ADSPOWER_PROXY_URL','ADSPOWER_PROXY_URL_FILE'))
            body=payload(a,proxy)
            if not a.execute:out={'dry_run':True,'name':a.name,'group_id':a.group_id,'proxy_type':proxy['proxy_type'],'proxy_credentials':'[REDACTED]'}
            else:
                data=call(a.api_base,'/api/v1/user/create','POST',body)
                if not data.get('id'):raise SafeError('Create response missing profile ID; inspect profiles before retrying.')
                out={'profile_id':data['id'],'created':True,'launched':False}
        else:
            if not a.profile_id.isalnum():raise SafeError('Invalid profile ID')
            if not a.execute:out={'dry_run':True,'action':a.command,'profile_id':a.profile_id}
            else:
                call(a.api_base,'/api/v1/browser/'+a.command,params={'user_id':a.profile_id})
                out={'submitted':True,'action':a.command,'profile_id':a.profile_id}
        print(json.dumps(out,indent=2));return 0
    except (SafeError,ValueError,OSError):
        print('Operation failed; check input, Local API access and app status. Sensitive details suppressed.',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
