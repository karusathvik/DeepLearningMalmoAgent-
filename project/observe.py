
import json

#gives the observation as a dictonary where we have: 
#dict res = name : {x, y, z, life, yaw, pitch}
def get_world_state (world_state):
    if world_state.number_of_observations_since_last_state > 0:
        obst = json.loads(world_state.observations[-1].text)['entities']
    res = {}

    for entity in obst:
        name = entity['name']
        res[name] = {
            'x': entity.get('x'),
            'y': entity.get('y'),
            'z': entity.get('z'),
            'yaw': entity.get('yaw'),
            'life': entity.get('life'),  # could be None for items like 'diamond'
            'pitch': entity.get('pitch')
        }
    return res    



