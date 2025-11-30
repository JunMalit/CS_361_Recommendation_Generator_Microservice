import zmq
import json
import time

SOCKET_ADDR = "tcp://localhost:5017"

TERMINATE_APP = False

# Sample data for testing the RECOMMENDATION microservice
SAMPLE_ALBUMS = [
    {"id": 1, "name": "Is This It", "tags": ["rock", "guitar"]},
    {"id": 2, "name": "Red", "tags": ["pop", "romance"]},
    {"id": 3, "name": "Korn", "tags": ["guitar", "metal"]},
]

SAMPLE_USERS = [
    {"id": 10, "ratings": {"1": 5, "2": 3}},
    {"id": 11, "ratings": {"1": 5, "3": 4}},
    {"id": 12, "ratings": {"2": 1, "3": 5}},
]

SAMPLE_CALL_1 = {
    "mode": "tags",
    "albums": SAMPLE_ALBUMS,
    "tags": ["guitar"],
}

SAMPLE_CALL_2 = {
    "mode": "similar_users",
    "albums": SAMPLE_ALBUMS,
    "users": SAMPLE_USERS,
    "user_id": 10,
}


def runClient(call):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(SOCKET_ADDR)

    sample_json = json.dumps(call)

    socket.send_string(sample_json)

    response = socket.recv()
    data = json.loads(response.decode())

    print(f"Microservice returned: {data}")

    if TERMINATE_APP:
        print("Terminating app program.")
        socket.send_string("Q")

    context.destroy()


if __name__ == "__main__":
    TERMINATE_APP = False
    runClient(SAMPLE_CALL_1)
    TERMINATE_APP = True
    runClient(SAMPLE_CALL_2)
