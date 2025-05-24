import json

def get_world_state(world_state):
    res = {}
    if world_state.number_of_observations_since_last_state > 0:
        obs_text = world_state.observations[-1].text
        entities = json.loads(obs_text).get('entities', [])
        for entity in entities:
            name = entity.get('name')
            if name:
                res[name] = {
                    'x': entity.get('x'),
                    'z': entity.get('z'),
                    'life': entity.get('life')  # may be None for items
                }
    return res
 