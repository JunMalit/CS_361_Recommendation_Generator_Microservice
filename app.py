import json
import zmq

SOCKET_ADDR = "tcp://*:5017"


def recommend_by_tags(albums, input_tags):
    """
    Given a list of tags, return albums that share any of those tags.
    Sort by # of shared tags (descending).
    """
    input_tags = set(tag.lower().strip() for tag in input_tags)

    # store first so program can sort before returning
    results = []
    for album in albums:
        album_tags = set(tag.lower().strip() for tag in album.get("tags", []))
        shared = input_tags.intersection(album_tags)

        if shared:
            results.append({"album": album, "shared_tags_count": len(shared)})

    # sort by number of shared tags (descending)
    results.sort(key=lambda album: album["shared_tags_count"], reverse=True)

    # return album objects
    return [r["album"] for r in results]


# Return all users who share at least one identical rating with the target user.
def get_similar_users(users, target_user_id, target_ratings):
    similar = []

    for user in users:
        if user["id"] == target_user_id:
            continue

        other_ratings = user.get("ratings", {})

        if any(
            album_id in other_ratings and other_ratings[album_id] == rating
            for album_id, rating in target_ratings.items()
        ):
            similar.append(user)

    return similar


#  get albums that the any of the given users rated >= 4
def get_user_favorites(users, target_ratings):
    favorites = []
    for user in users:
        for album_id, rating in user.get("ratings", {}).items():
            if rating >= 4 and album_id not in target_ratings:
                favorites.append(int(album_id))
    return favorites


def recommend_by_similar_users(albums, users, target_user_id):
    # get user who is performing the search
    target_user = next((u for u in users if u["id"] == target_user_id), None)
    if not target_user:
        return []

    target_ratings = target_user.get("ratings", {})

    similar_users = get_similar_users(users, target_user_id, target_ratings)

    # find what the other user rated >= 4
    recommended_albums = get_user_favorites(similar_users, target_ratings)

    return [album for album in albums if album["id"] in recommended_albums]


def call(data):

    mode = data.get("mode", "")

    if mode == "tags":
        albums = data.get("albums", [])
        tags = data.get("tags", [])
        return recommend_by_tags(albums, tags)

    elif mode == "similar_users":
        albums = data.get("albums", [])
        users = data.get("users", [])
        user_id = data.get("user_id", None)
        return recommend_by_similar_users(albums, users, user_id)

    else:
        return []


def server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(SOCKET_ADDR)

    while True:
        message = socket.recv()
        full_msg = message.decode()

        if full_msg == "Q":
            break

        json_data = json.loads(full_msg)
        result = call(json_data)

        socket.send_string(json.dumps({"result": result}))

    context.destroy()
    socket.close()


if __name__ == "__main__":
    server()
