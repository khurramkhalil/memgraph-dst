import time
import random
import mgclient
from demo_memgraph_helper_func import create_friendly_node, create_enemy_node, nodes_index, from_x_to_y_connection, \
    create_index, create_relations, update_friendly_node, update_enemy_node, del_graph, delete_friendly_node, \
    delete_enemy_node, generate_friends_and_enemies, delete_nodes_from_rtree, insert_nodes_into_rtree, from_x_to_y_single_connection, from_x_to_y_single_connection_one, \
    create_territory_node

random.seed(40)

# Delete Previous Graph (if any)
del_graph()

# Connect to Memgraph
conn = mgclient.connect(host='127.0.0.1', port=7687)
cursor = conn.cursor()

# Parameters
GRID_SIZE = 100
num_samples = 10

# Create nodes with the "Territory" label in Memgraph
create_territory_node(GRID_SIZE)

t0 = time.time()
# Create dictionaries for friends and enemies
sample_points_friends, friends, sample_points_enemies, enemys = generate_friends_and_enemies(GRID_SIZE, num_samples)

# Create Initial Friendly and Enemy Graph
create_friendly_node(friends)
create_enemy_node(enemys)

print(f'Time Taken for Initial Graph Construction: {time.time() - t0}')

# Perform Indexing on Enemy and Friendly ids
create_index()
enemy_idx = nodes_index(enemys)
t1 = time.time()
# Create an r-tree index for enemy nodes


t=time.time()

# For each friend, find the nearest enemy and vice versa
friend_to_enemy = from_x_to_y_connection(friends, enemy_idx)
friend_to_enemy_unique = from_x_to_y_single_connection_one(friends, enemy_idx)
friend_to_enemy_single = from_x_to_y_single_connection(friends, enemys, enemy_idx)

t2 = time.time()
print(f'Time Taken for indexing and pairing: {t2 - t}')


# friend_to_enemy_single = from_x_to_y_single_connection(friends, enemys, enemy_idx)

# Create edges between neighboring friendly - enemy pair
create_relations(friend_to_enemy)

print(f'Time Taken for indexing and pairing: {t2 - t}')
print(f'Time Taken for constructing relations: {time.time() - t2}')

#######################
# Next instance details
#######################

t3 = time.time()
# IDs to be deleted
deleted_ids = list(range(int(num_samples * 0.1)))
filtered_friends = [friend for friend in friends if friend['id'] not in deleted_ids]
filtered_enemys = [enemy for enemy in enemys if enemy['id'] not in deleted_ids]

# Then delete these (freindly and enemy) nodes from the Memgraph database
delete_friendly_node(deleted_ids)
delete_enemy_node(deleted_ids)

print(f'Time Taken for Deleting Missing Nodes: {time.time() - t3}')

t4 = time.time()
# New IDs to be added
new_ids_from = int(num_samples * 0.9)
new_friends = [{"id": i + new_ids_from, "x": x, "y": y, "label": "next"} for i, (x, y) in enumerate(sample_points_friends[new_ids_from:])]
new_enemys = [{"id": i + new_ids_from, "x": x, "y": y, "label": "next"} for i, (x, y) in enumerate(sample_points_enemies[new_ids_from:])]

# Add new IDs in Memgraph database
create_friendly_node(new_friends)
create_enemy_node(new_enemys)

# Combine filtered data and new data
next_friends = filtered_friends + new_friends
next_enemys = filtered_enemys + new_enemys

print(f'Time Taken for Adding New Incoming Nodes: {time.time() - t4}')

t5 = time.time()
# IDs to be updated
up, down = int(num_samples * 0.3), int(num_samples * 0.4)
updated_ids = list(range(up, down))
update_friends = [{"id": i + up, "x": x, "y": y, "label": "next"} for i, (x, y) in enumerate(sample_points_friends[up:down])]
update_enemys = [{"id": i + up, "x": x, "y": y, "label": "next"} for i, (x, y) in enumerate(sample_points_enemies[up:down])]

# Update new values in Memgraph database
update_friendly_node(update_friends)
update_enemy_node(update_enemys)

# Updating incoming data of existing nodes
next_friends[up:down] = update_friends
next_enemys[up:down] = update_enemys

print(f'Time Taken for Updating Current Nodes: {time.time() - t5}')

###########################################
# ReCalculating Relations on Updated Graph
###########################################

t6 = time.time()

# update_enemy_idx = delete_nodes_from_rtree(enemy_idx, deleted_ids, enemys)
# update_enemy_idx = insert_nodes_into_rtree(update_enemy_idx, updated_ids, next_enemys)

# friend_to_enemy = from_x_to_y_connection(next_friends, update_enemy_idx)

# Create an r-tree index for enemy nodes
enemy_idx = nodes_index(next_enemys)

# For each friend, find the nearest enemy and vice versa
friend_to_enemy = from_x_to_y_connection(next_friends, enemy_idx)

t7 = time.time()
# Create edges between neighboring friendly - enemy pair
create_relations(friend_to_enemy)

t8 = time.time()
print(f'Time Taken for Indexing and Pairing On Next Instance: {t7 - t6}')
print(f'Time Taken for Constructing Relations On Next Instance: {t8 - t7}')

print('\n')
print(f'Total time taken: {(t8 - t0) / 2}')
