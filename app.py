import uuid
import json  
import boto3
from flask import Flask, request
import requests
from ec2_metadata import ec2_metadata
import threading
import jump
import xxhash 

current_instance_id = ec2_metadata.instance_id
memory = {}
instances_order = []
instances_health = {}
instances_ip = {}

alb_client = boto3.client('elbv2', region_name='us-east-2')
ec2_client = boto3.client('ec2', region_name='us-east-2')

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

def get_healthy_instances():
    response = alb_client.describe_target_health(TargetGroupArn=target_group_arn)
    print(response)
    for info in response["TargetHealthDescriptions"]:
        instances_health[info["Target"]["Id"]] = info["TargetHealth"]["State"]
        if(info["TargetHealth"]["State"] == "healthy"):
            instances_order.append(info["Target"]["Id"])
            if info["Target"]["Id"] not in instances_ip:
                data = ec2_client.describe_instances(InstanceIds=[info["Target"]["Id"]])
                print(data)
                instances_ip[info["Target"]["Id"]] = data["Reservations"][0]["Instances"][0]["PrivateIpAddress"]
    instances_order.sort()    

set_interval(get_healthy_instances, 30)

def reorganize():
    for key in memory:
        data = memory[key]["data"]
        expiration_date = memory[key]["expiration_date"]
        v_node_id = xxhash.xxh64(key ).intdigest() % 1024
        node_index = jump.hash(v_node_id, len(instances_order))
       
        if(len(instances_order) - 1 == node_index):
            next_node_index = 0
        else:
            next_node_index = node_index + 1
        if(instances_order[node_index] != current_instance_id):
            requests.get("http://" + instances_ip[instances_order[node_index]] + ":5000/putInternal?str_key="+key+"&data="+data+"&expiration_date="+expiration_date)
        if(instances_order[next_node_index] != current_instance_id):
            requests.get("http://" + instances_ip[instances_order[next_node_index]] + ":5000/putInternal?str_key="+key+"&data="+data+"&expiration_date="+expiration_date)
        if((instances_order[next_node_index] != current_instance_id) and (instances_order[node_index] != current_instance_id)):
            memory.pop(key, None)
        


app = Flask(__name__)

@app.route('/healthCheck')
def healthCheck():
    return "healthy", 200

@app.route('/put')
def put():
    str_key = request.args.get('str_key')
    data = request.args.get('data')
    expiration_date = request.args.get('expiration_date')
    v_node_id = xxhash.xxh64(str_key ).intdigest() % 1024
    node_index = jump.hash(v_node_id, len(instances_order))
    if(len(instances_order) - 1 == node_index):
        next_node_index = 0
    else:
        next_node_index = node_index + 1
    if(instances_order[node_index] != current_instance_id):
        requests.get("http://" + instances_ip[instances_order[node_index]] + ":5000/putInternal?str_key="+str_key+"&data="+data+"&expiration_date="+expiration_date)
    if(instances_order[next_node_index] != current_instance_id):
        requests.get("http://" + instances_ip[instances_order[next_node_index]] + ":5000/putInternal?str_key="+str_key+"&data="+data+"&expiration_date="+expiration_date)
    if((instances_order[next_node_index] == current_instance_id) or (instances_order[node_index] == current_instance_id)):
        memory[str_key] = {
            "data": data,
            "expiration_date": expiration_date
        }
    
    return "data saved!", 200

@app.route('/putInternal')
def putInternal():
    str_key = request.args.get('str_key')
    data = request.args.get('data')
    expiration_date = request.args.get('expiration_date')

    memory[str_key] = {
        "data": data,
        "expiration_date": expiration_date
    }
    
    return "data saved!", 200


@app.route('/get')
def get():
    final_response = "null"
    str_key = request.args.get('str_key')
    v_node_id = xxhash.xxh64(str_key ).intdigest() % 1024
    node_index = jump.hash(v_node_id, len(instances_order))
    if(len(instances_order) - 1 == node_index):
        next_node_index = 0
    else:
        next_node_index = node_index + 1
    if((instances_order[next_node_index] == current_instance_id) or (instances_order[node_index] == current_instance_id)):
        if str_key not in memory:
            return "null", 200
        else:
            return memory[str_key]["data"], 200
    else:
        request_from_node = requests.get("http://" + instances_ip[instances_order[node_index]] + ":5000/getInternal?str_key="+str_key)
        request_from_next_node = requests.get("http://" + instances_ip[instances_order[next_node_index]] + ":5000/getInternal?str_key="+str_key)
        if(request_from_node.status_code == 200 and request_from_node.text != 'null'):
            final_response = request_from_node.text
        
        if(request_from_next_node.status_code == 200 and request_from_next_node.text != 'null'):
            final_response = request_from_next_node.text
        

    return final_response, 200

@app.route('/getInternal')
def getInternal():
    str_key = request.args.get('str_key')

    if str_key not in memory:
        return "null", 200
    else:
        return memory[str_key]["data"], 200

@app.route('/newNodeAdded')
def newNodeAdded():
    instances_order = []
    instances_health = {}
    instances_ip = {}
    t = threading.Timer(60, reorganize)
    t.start()
    return "reorganizing in 60 seconds", 200
