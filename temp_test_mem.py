# import mgclient

# # Create a new connection to Memgraph
# conn = mgclient.connect(
#     host='127.0.0.1',
#     port=7687,
# )

# # Create a new cursor
# cursor = conn.cursor()

# # Execute a Cypher query
# cursor.execute('MATCH (n:Friendly) RETURN n LIMIT 5')

# # Fetch the results
# for row in cursor.fetchall():
#     print(row)

# # Close the connection
# conn.close()

import mgclient

# Create a new connection to Memgraph
conn = mgclient.connect(host='127.0.0.1', port=7687)

# Create a new cursor
cursor = conn.cursor()

# Prepare the data
data = [
    {"id": i, "lat": i, "lon": i, "time": i}
    for i in range(1, 5000)
]

# Prepare the Cypher query
query = """
UNWIND $props AS map
CREATE (n:Friendly) SET n = map
"""

# Execute the Cypher query
cursor.execute(query, {'props': data})

# Commit the transaction
conn.commit()

# Close the connection
conn.close()
