from typing import List

import requests

from framework.config import Client
from framework.core.policy import Policy


def getPolicy(policy_list: List[str]):
    policyIdStr = '|'.join(policy_list)
    params = {
        'policyIdStr': policyIdStr,
        'processName': Client.PROCESS_NAME
    }
    response = requests.get('http://spider-framework:6048/policy/getPolicysByPolicyIdStr', params=params)
    items = response.json()
    data = list()
    for item in items:
        policy = Policy(**item)
        data.append(policy)
    return data


def getPolicyByProcessName():
    params = {
        'processName': Client.PROCESS_NAME
    }
    response = requests.get('http://spider-framework:6048/policy/getPolicys', params=params)
    items = response.json()
    data = list()
    for item in items:
        policy = Policy(**item)
        data.append(policy)
    return data
