import uuid
import json  
import boto3
from flask import Flask, request
from ec2_metadata import ec2_metadata
import threading


current_instance_id = ec2_metadata.instance_id
memory = {}
instances_health = {}

alb_client = boto3.client('elbv2', region_name='us-east-2')
ec2_client = boto3.resource('ec2', region_name='us-east-2')

targetGroupArn_file = open("targetGroupArn.txt", "r")
target_group_arn = targetGroupArn_file.read()
targetGroupArn_file.close()

loadBalancerArnloadBalancerArn_file = open("loadBalancerArn.txt", "r")
load_balancer_arn = loadBalancerArnloadBalancerArn_file.read()
loadBalancerArnloadBalancerArn_file.close()


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def get_healthy_instances(alb_client, target_group_arn):
    response = alb_client.describe_target_health(TargetGroupArn=target_group_arn)
    for info in response.TargetHealthDescriptions:
        instances_health[info.Target.Id] = info.TargetHealth.State

set_interval(get_healthy_instances, 10)

app = Flask(__name__)

@app.route('/healthCheck')
def healthCheck():
    return "healthy", 200

@app.route('/put')
def put():
    str_key = request.args.get('str_key')
    data = request.args.get('data')
    expiration_date = request.args.get('expiration_date')
    memory["str_key"] = {
        "data": data,
        "expiration_date": expiration_date
    }
    return get_healthy_instances, 200


# @app.route('/exit')
# def exit():
#     id = request.args.get("ticketId")
#     ticket_str = r.get(id)
#     if ticket_str is None:
#         return "No such ticket", 404

#     ticket = json.loads(ticket_str)

#     if "exit" in ticket:
#         return ticket_str, 406

#     entry_time = datetime.fromisoformat(ticket["entry"])
#     exit = datetime.now()
#     diff_in_minutes = int((exit - entry_time).total_seconds() / 60)
#     charges = diff_in_minutes / 15
#     if diff_in_minutes % 15 != 0:
#         charges += 1
    
#     ticket["exit"] = exit.isoformat()
#     ticket["chargs"] = charges
#     ticket["total_cost"] = charges * 2.5

#     r.set(id, json.dumps(ticket))

#     return ticket

