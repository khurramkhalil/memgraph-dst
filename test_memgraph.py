import mgclient

# Connect to Memgraph 
conn = mgclient.connect(host='127.0.0.1', port=7687)
# Create a new cursor
cursor = conn.cursor()

# Parameters
GRID_SIZE = 100
BORDER_DEPTH = 2
INNER_STEP = 5

# Helper functions

def create_node(data):
  query = """
  UNWIND $props AS map
  CREATE (n:Territory) SET n = map
  """
  cursor.execute(query, {'props': data})
  conn.commit()
  
def get_node(query):
  cursor.execute(query)
  results = cursor.fetchall()
  return results
  
def connect_nodes():
    query = """
    MATCH (b:Territory {label: 'border'}), (i:Territory {label: 'inner'})
    WITH b, i, sqrt((b.x - i.x)*(b.x - i.x) + (b.y - i.y)*(b.y - i.y)) AS distance
    ORDER BY distance ASC
    WITH b, collect(i)[0] AS closest_inner_node
    CREATE (b)-[:CONNECTS_TO]->(closest_inner_node)
    """
    cursor.execute(query)
    conn.commit()
    
def set_terrain(x_bound, y_bound, name):
    # Set terrain based on (x,y)
    query = """
    MATCH (n:Territory)
    WHERE n.x < ($x_bound) AND n.y > ($y_bound)
    SET n.terrain = $terrain
    """
    cursor.execute(query, {'x_bound':x_bound, 'y_bound': y_bound, 'terrain': name})
    conn.commit()
    
def set_defense(sites):
    query = """
    UNWIND $sites AS site
    MATCH (n:Territory {x: site[0], y: site[1], label: 'inner'})
    SET n.defense = 'sam_site'
    """
    cursor.execute(query, {'sites': sites})
    conn.commit()
    
def set_resources(n):
    cursor.execute("""MATCH (n:Territory {x: $x, y: $y})
                 SET n.resources = $resources",
                 x=n.x, y=n.y, resources="fuel_depot""")
    conn.commit()

# Create border nodes
border = [
    {"x": x, "y": y, "label": "border"}
    for x in range(GRID_SIZE)
    for y in range(BORDER_DEPTH)
    if x + y <= GRID_SIZE
]

create_node(border)
query = "MATCH (n:Territory) RETURN n"
border_nodes = get_node(query)


# Create inner nodes
inner = [
    {"x": x, "y": y, "label": "inner"}
    for x in range(0, GRID_SIZE, INNER_STEP)
    for y in range(0, GRID_SIZE, INNER_STEP)
    if x + y <= GRID_SIZE
]

create_node(inner)
query = "MATCH (n:Territory) WHERE n.label = 'inner' RETURN n"
inner_nodes = get_node(query)

# Connect closest border with closest inner nodes
connect_nodes()

# Set node properties
set_terrain(GRID_SIZE/2.8, GRID_SIZE/1.2, 'mountain')
sites = [[80, 20, 'west'], [50, 50, 'mid'], [10, 90, 'south']]
set_defense(sites)

# set_resources()

# Close connection  
conn.close()
















