import time
import random

import mgclient
from memgraph_helper_func import create_friendly_node, create_enemy_node,  \
    nodes_index, from_x_to_y_connection, create_index, create_relations, \
    update_friendly_node, update_enemy_node, del_graph


# Delete Previous Graph (if any)
del_graph()

# Connect to Memgraph 
conn = mgclient.connect(host='127.0.0.1', port=7687)
# Create a new cursor
cursor = conn.cursor()

# Parameters
GRID_SIZE = 100
num_samples = 100

# FRIENDS
# Generate a grid that satisfies the condition x + y <= GRID_SIZE
grid = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if x + y <= GRID_SIZE]
# Randomly sample num_samples points from the grid
sample_points = random.sample(grid, num_samples)
# Create the dictionary
friends = [{"id": i, "x": x, "y": y, "label": "current"} for i, (x, y) in enumerate(sample_points[:int(num_samples * 0.9)])]

# ENEMY
# Generate a grid that satisfies the condition x + y >= GRID_SIZE
grid = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if x + y >= GRID_SIZE]
# Randomly sample num_samples points from the grid
sample_points = random.sample(grid, num_samples)
# Create the dictionary
enemys = [{"id": i, "x": x, "y": y, "label": "current"} for i, (x, y) in enumerate(sample_points[:int(num_samples * 0.9)])]

t0 = time.time()
# Create Initial Friendly and Enemy Graph
create_friendly_node(friends)
create_enemy_node(enemys)

print(f'Time Taken for Initial Graph Construction for Friendly and Enemy: {time.time() - t0}')

# Perform Indexing on Enemy and Friendly ids
create_index()

t1 = time.time()
# Create an r-tree index for enemy nodes
enemy_idx = nodes_index(enemys)

# For each friend, find the nearest enemy and vice versa
friend_to_enemy = from_x_to_y_connection(friends, enemy_idx)

t2 = time.time()
# Create edges between neighbouring friendly - enemy pair
create_relations(friend_to_enemy)

print(f'Time Taken for indexing and pairing: {t2 - t1}')
print(f'Time Taken for constructing relations: {time.time() - t2}')

#######################
# Next instance details
#######################

t3 = time.time()
# IDs to be deleted
deleted_ids = list(range(int(num_samples * 0.1)))
filtered_friends = [friend for friend in friends if friend['id'] not in deleted_ids]
filtered_enemys = [enemy for enemy in enemys if enemy['id'] not in deleted_ids]

# Then delete these nodes from the Memgraph database
query = "MATCH (n:Friendly) WHERE n.id IN $deleted_ids DETACH DELETE n"
cursor.execute(query, {'deleted_ids': deleted_ids})
conn.commit()

query = "MATCH (n:Enemy) WHERE n.id IN $deleted_ids DETACH DELETE n"
cursor.execute(query, {'deleted_ids': deleted_ids})
conn.commit()

print(f'Time Taken for Deleting Missing Nodes: {time.time() - t3}')


t4 = time.time()
# New IDs to be added
up, down = int(num_samples * 0.9), int(num_samples * 1.02)
new_ids = list(range(up, down))
new_friends = [{"id": i + up, "x": x, "y": y, "label": "next"} for i, (x, y) in enumerate(sample_points[up:])]
new_enemys = [{"id": i + up, "x": x, "y": y, "label": "next"} for i, (x, y) in enumerate(sample_points[up:])]

# Add new IDs in memgraph database
create_friendly_node(new_friends)
create_enemy_node(new_enemys)

next_friends = filtered_friends + new_friends
next_enemys = filtered_enemys + new_enemys

print(f'Time Taken for Adding New Incoming Nodes: {time.time() - t4}')

t5 = time.time()
# IDs to be updated
up, down = int(num_samples * 0.3), int(num_samples * 0.41)
update_friends = [{"id": i + up, "x": x, "y": y, "label": "next"} for i, (x, y) in enumerate(sample_points[up:down])]
update_enemys = [{"id": i + up, "x": x, "y": y, "label": "next"} for i, (x, y) in enumerate(sample_points[up:down])]

# Update new values in memgraph database
update_friendly_node(update_friends)
update_enemy_node(update_enemys)

print(f'Time Taken for Updating Current Nodes: {time.time() - t5}')

next_friends[up:down] = update_friends
next_enemys[up:down] = update_enemys

###########################################
# ReCalculating Relations on updated Graph
###########################################

t6 = time.time()
# Create an r-tree index for enemy nodes
enemy_idx = nodes_index(next_enemys)

# For each friend, find the nearest enemy and vice versa
friend_to_enemy = from_x_to_y_connection(next_friends, enemy_idx)

t7 = time.time()
# Create edges between neighbouring friendly - enemy pair
create_relations(friend_to_enemy)

t8 = time.time()
print(f'Time Taken for indexing and pairing On Next Instance: {t7 - t6}')
print(f'Time Taken for constructing relations On Next Instance: {t8 - t7}')

print('\n')
print(f'Total time taken: {(t8 - t0) / 2}')


















