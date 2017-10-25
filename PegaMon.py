#!/usr/bin/python
import sys, os, datetime
import configparser
import xml.etree.ElementTree as ET
from subprocess import Popen, PIPE
import pickle
import json


def get_pega_status_xml(common_config, node_config):
    username = common_config['username']
    password = common_config['password']
    java_path = common_config['java_path']
    jar = common_config['jar']
    hostname = common_config['hostname']
    port = common_config['port']
    node_id = node_config['node_id']
    node_name = node_config['node_name']

    jar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), jar)
    proc = Popen([java_path, '-jar', jar_path, hostname + ':' + port, node_name, node_id, username, password], stdout=PIPE)
    res = proc.communicate()
    if proc.returncode:
        print(res[1])
    xml = res[0].decode("utf-8").replace('\n', '')
    tree = ET.ElementTree(ET.fromstring(xml))
    return tree


def get_agents_status_from_pega(config):
    sections = [section for section in config.sections() if section.lower() != 'common']
    agent_status = {}
    common_config = config['common']

    for section in sections:
        agent_status.update({section: {}})
        node_config = config[section]
        root = get_pega_status_xml(common_config, node_config).getroot()

        monitored_agents = node_config['monitored_agents'].replace(', ', ',').replace(' ,', ',').split(',')
        for item in root.findall('Agents/Agent'):
            if item.find('Description').text in monitored_agents:
                agent_status.get(section).update({item.find('Description').text: item.find('Runnable').text});

    return agent_status


def put_agents_status_to_file(file_path, agent_status):
    with open(file_path, 'wb') as f:
        pickle.dump(agent_status, f)


def get_agents_status_from_file(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def get_discovery_json(agent_status):
    data = {"data": []}
    for node in agent_status.items():
        for agent in node[1].keys():
            data.get('data').append({'{#AGENT}': "{0}:{1}".format(node[0],agent)})

    return json.dumps(data).replace(' ', '')


def main():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)) , u'config.conf')
    config.read(config_path)
    common_config = config['common']
    cache_file_path = common_config['cache_file_path']
    cache_file_ttl = common_config['cache_file_ttl']

    if os.path.isfile(cache_file_path):
        file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(cache_file_path))
        if datetime.datetime.now() - file_modified > datetime.timedelta(seconds=int(cache_file_ttl)):
            agent_status = get_agents_status_from_pega(config)
            put_agents_status_to_file(cache_file_path, agent_status)
        else:
            agent_status = get_agents_status_from_file(cache_file_path)
    else:
        agent_status = get_agents_status_from_pega(config)
        put_agents_status_to_file(cache_file_path, agent_status)

    if len(sys.argv) == 1:
        print get_discovery_json(agent_status)
    else:
        node, agent = sys.argv[1].split(':')
        try:
            print agent_status.get(node).get(agent)

        except:
            print 'invalid key'




if __name__ == '__main__':
    sys.exit(main())
