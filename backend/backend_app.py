from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    # Read optional sorting parameters
    sort_field = request.args.get("sort")
    direction = request.args.get("direction")

    # Without sorting parameters, return the posts in their original order
    if sort_field is None and direction is None:
        return jsonify(POSTS)

    # Validate the provided sorting parameters
    if sort_field not in ("title", "content"):
        return jsonify({"error": "Invalid sort field. Allowed values are 'title' or 'content'."}), 400
    if direction not in ("asc", "desc"):
        return jsonify({"error": "Invalid direction. Allowed values are 'asc' or 'desc'."}), 400

    # Sort a copy so the original order is preserved
    sorted_posts = sorted(POSTS, key=lambda post: post[sort_field].lower(), reverse=(direction == "desc"))
    return jsonify(sorted_posts)


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    # Validate required fields and report any that are missing
    missing_fields = [field for field in ("title", "content") if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Generate a new unique integer ID
    new_id = max((post["id"] for post in POSTS), default=0) + 1
    new_post = {"id": new_id, "title": data["title"], "content": data["content"]}
    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    # Read search terms from the query parameters
    title_query = request.args.get("title", "")
    content_query = request.args.get("content", "")

    # Keep posts whose title or content contains the given terms
    matching_posts = [
        post for post in POSTS
        if title_query.lower() in post["title"].lower()
        and content_query.lower() in post["content"].lower()
    ]

    return jsonify(matching_posts)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    # Look up the post by its ID
    post = next((post for post in POSTS if post["id"] == post_id), None)
    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    # Remove the post from the list
    POSTS.remove(post)
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    # Look up the post by its ID
    post = next((post for post in POSTS if post["id"] == post_id), None)
    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    # Update only the provided fields, keep the old values otherwise
    data = request.get_json()
    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])

    return jsonify(post), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
