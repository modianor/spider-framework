from typing import List

import requests

from core.policy import Policy


def getPolicy(policy_list: List[str]):
    policyIdStr = '|'.join(policy_list)
    params = {
        'policyIdStr': policyIdStr
    }
    response = requests.get('http://spider-framework:6048/policy/getPolicysByPolicyIdStr', params=params)
    items = response.json()
    data = list()
    for item in items:
        policy = Policy(**item)
        data.append(policy)
    return data
