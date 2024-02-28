import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List

from database import Payment


class GroupTypes(str, Enum):
    day = 'day'
    hour = 'hour'
    month = 'month'


def gen_all_interval(dt_from: datetime, dt_upto: datetime, group_type: GroupTypes) -> List[datetime]:
    result, interval = list(), None

    match group_type:
        case GroupTypes.hour:
            current_date = dt_from.replace(minute=0, second=0)
            interval = timedelta(hours=1)
        case GroupTypes.day:
            current_date = dt_from.replace(hour=0, minute=0, second=0)
            interval = timedelta(days=1)
        case GroupTypes.month:
            current_date = dt_from.replace(hour=0, minute=0, second=0, day=1)
        case _:
            raise ValueError

    while current_date <= dt_upto:
        result.append(current_date)
        if group_type != GroupTypes.month:
            current_date += interval
        else:
            next_month = (current_date.month + 1) % 12
            if next_month == 0:
                next_month = 12
            current_date = current_date.replace(
                month=next_month,
                year=current_date.year + ((current_date.month + 1) // 12)
            )
    return result


def from_json_format(label: str) -> dict:
    data = json.loads(label)
    return {'dt_from': datetime.strptime(data['dt_from'], '%Y-%m-%dT%H:%M:%S'),
            'dt_upto': datetime.strptime(data['dt_upto'], '%Y-%m-%dT%H:%M:%S'),
            'group_type': GroupTypes(data['group_type'])}


def gen_pipeline(template_path: str | Path, dt_from: datetime, dt_upto: datetime, group_type: GroupTypes) -> list:
    with open(template_path) as file:
        pipeline = json.loads(file.read())
    pipeline[0]['$match']['dt']['$gte'] = dt_from
    pipeline[0]['$match']['dt']['$lte'] = dt_upto
    pipeline[2]['$group']['_id'] = f'${group_type.value}'

    return pipeline


def arrange_zeros(data, intervals) -> dict:
    for i in range(len(intervals)):
        str_format = intervals[i].strftime('%Y-%m-%dT%H:%M:%S')
        if (i + 1) > len(data['labels']) or str_format != data['labels'][i]:
            data['dataset'].insert(i, 0)
            data['labels'].insert(i, str_format)
    return data


def convert_aggregation(data) -> dict:
    result = {"dataset": [value['value'] for value in data],
              "labels": [value['_id'].strftime('%Y-%m-%dT%H:%M:%S') for value in data]}

    return result


async def aggregate_by(dt_from: datetime, dt_upto: datetime, group_type: GroupTypes) -> dict:
    all_intervals = gen_all_interval(dt_from, dt_upto, group_type)
    pipeline = gen_pipeline('aggreagations/payments.json', dt_from, dt_upto, group_type)
    data = await Payment.aggregate(pipeline).to_list()
    data = convert_aggregation(data)
    data = arrange_zeros(data, all_intervals)
    return data
