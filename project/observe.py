import json

def create_command(action, number):
    return "{}".format(action) + " " + "{}".format(number)

def get_world_state(world_state):
    """
    Parse Malmo’s WorldState into a flat dict with keys:
      agentx, agenty, health,
      d1x, d1y, d2x, d2y, d3x, d3y, d4x, d4y, d5x, d5y,
      d1,  d2,  d3,  d4,  d5,
      zx, zy,
      done
    """

    state = {
        'agentx': 0.0, 'agenty': 0.0, 'health': 0.0, 'd1x': 0.0, 'd1y': 0.0, 'd2x': 0.0, 'd2y': 0.0, 'd3x': 0.0, 'd3y': 0.0, 'd4x': 0.0, 'd4y': 0.0, 'd5x': 0.0, 'd5y': 0.0, 'd1': 1, 'd2': 1, 'd3': 1, 'd4': 1, 'd5': 1, 'zx': 0.0, 'zy': 0.0, 'done':     not world_state.is_mission_running
    }

    if world_state.number_of_observations_since_last_state > 0:
        obs = json.loads(world_state.observations[-1].text)
        ents = obs.get('entities', [])

        # Agent (assume exactly one named 'Agent')
        agent = next((e for e in ents if e.get('name')=='Agent'), None)
        if agent:
            state['agentx'] = agent['x']
            state['agenty'] = agent['z']   # Malmo’s “y” is vertical; here we use x/z as our 2D plane
            state['health'] = agent.get('life', 0.0)

        # Diamonds (assume names 'Diamond1'…'Diamond5')
        diamond_ents = [e for e in ents if e.get('name') == 'Diamond']
        for idx, ent in enumerate(diamond_ents[:5], start=1):
            state['d{}x'.format(idx)] = ent['x']
            state['d{}y'.format(idx)] = ent['z']
            state['d{}'.format(idx)]  = 0

        # Zombie (assume exactly one named 'Zombie')
        zombie = next((e for e in ents if e.get('name')=='Zombie'), None)
        if zombie:
            state['zx'] = zombie['x']
            state['zy'] = zombie['z']

    return state