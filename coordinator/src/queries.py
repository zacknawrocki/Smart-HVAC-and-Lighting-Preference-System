'''
queries.py
'''


class Queries(object):
    """
    This enum class contains SQLITE query strings which are used in
      calc_temp.py and coordinator.py
    """
    CREATE_TABLE_USERS = "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, preference REAL);"
    CREATE_TABLE_SENSORS = "CREATE TABLE sensors (id INTEGER PRIMARY KEY, x_pos REAL, y_pos REAL, temperature REAL);"
    CREATE_TABLE_NODES = "CREATE TABLE nodes (id INTEGER PRIMARY KEY, x_pos REAL, y_pos REAL, estimated_temp REAL, current_user_id INTEGER, temp_offset INTEGER);"
    CREATE_TABLE_AMBIENT = "CREATE TABLE ambient (id INTEGER PRIMARY KEY AUTOINCREMENT, temperature REAL);"
    
    CREATE_TABLE_MEETINGS = "CREATE TABLE meetings (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, start TEXT, finish TEXT, attendees TEXT, avgtemp INTEGER, phpc_time TEXT);"
    CREATE_TABLE_HISTORICAL_USERS = "CREATE TABLE historical_users (uid INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, id INTEGER, name TEXT, preference REAL);"
    CREATE_TABLE_HISTORICAL_NODES = "CREATE TABLE historical_nodes (uid INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP , id INTEGER, current_user_id INTEGER, estimated_temp REAL);"
    CREATE_TABLE_HISTORICAL_SENSORS = "CREATE TABLE historical_sensors (uid INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP , id INTEGER, temperature REAL);"
    CREATE_TABLE_HISTORICAL_OPTIMIZED = "CREATE TABLE historical_optimized (uid INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, temperature REAL);"

    INSERT_USER = "INSERT INTO 'users' ('name', 'preference') VALUES (?, ?);"    
    INSERT_SENSOR = "INSERT INTO 'sensors' ('id', 'x_pos', 'y_pos', 'temperature') VALUES (?, ?, ?, ?);"
    INSERT_NODE = "INSERT INTO 'nodes' ('id', 'x_pos', 'y_pos', 'current_user_id', 'temp_offset') VALUES (?, ?, ?, ?, ?);"
    INSERT_AMBIENT = "INSERT INTO 'ambient' ('temperature') VALUES (?);"
    INSERT_HISTORICAL_USER = "INSERT INTO 'historical_users' ('id', 'name', 'preference') VALUES (?, ?, ?);"
    INSERT_HISTORICAL_NODE = "INSERT INTO 'historical_nodes' ('id', 'current_user_id', 'estimated_temp') VALUES (?, ?, ?);"
    INSERT_HISTORICAL_SENSOR = "INSERT INTO 'historical_sensors' ('id', 'temperature') VALUES (?, ?);"
    INSERT_HISTORICAL_OPTIMIZED = "INSERT INTO 'historical_optimized' ('temperature') VALUES (?);"    
    INSERT_MEETING = "INSERT INTO 'meetings' ('id', 'name', 'start', 'finish', 'attendees', 'avgtemp', 'phpc_time') VALUES (?, ?, ?, ?, ?, ?, ?);"

    UPDATE_NODE = "UPDATE 'nodes' SET current_user_id = ? WHERE id = ?;"
    UPDATE_OFFSET = "UPDATE 'nodes' SET temp_offset = ? WHERE id = ?;"
    UPDATE_NODE_TEMP = "UPDATE 'nodes' SET estimated_temp = ? WHERE id = ?;"
    UPDATE_PREFERENCE = "UPDATE 'users' SET preference = ? WHERE id = ?;"
    UPDATE_SENSOR = "UPDATE 'sensors' SET temperature = ? WHERE id = ?;"

    DELETE_NODE = "DELETE FROM 'nodes' WHERE id = ?;"
    DELETE_USER = "DELETE FROM 'users' WHERE id = ?;"    
    DELETE_MEETING = "DELETE FROM 'meetings' WHERE id = ?;"

    GET_USERS = "SELECT * FROM 'users';"
    GET_NODES = "SELECT * FROM 'nodes';"
    GET_MEETINGS = "SELECT * FROM 'meetings';"
    GET_NODE_TEMPERATURE = "SELECT estimated_temp FROM nodes WHERE id = ?;"
    GET_NODE_OFFSET = "SELECT temp_offset FROM nodes WHERE id = ?;"
    GET_SENSORS = "SELECT * FROM 'sensors';"
    GET_AMBIENT = "SELECT * FROM 'ambient';"
    GET_TABLES = "SELECT name FROM sqlite_master WHERE type='table';"
    GET_USER_ID = "SELECT id FROM users WHERE name = ?;"

    DROP_TABLE_NODES = "DROP TABLE 'nodes';"
    DROP_TABLE_SENSORS = "DROP TABLE 'sensors';"

