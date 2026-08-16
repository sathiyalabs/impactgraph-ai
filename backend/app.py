from pathlib import Path

from flask import Flask, jsonify, request

from ml.predict import predict_commit


app = Flask(__name__)


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@app.get("/api/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "ImpactGraph AI",
        }
    )


@app.post("/api/predict")
def predict():

    data = request.get_json(silent=True)

    if not data:
        return jsonify(
            {
                "error": "Request body must be JSON."
            }
        ), 400

    repository = data.get("repository")
    commit = data.get("commit")

    if not repository:
        return jsonify(
            {
                "error": "Missing 'repository'."
            }
        ), 400

    if not commit:
        return jsonify(
            {
                "error": "Missing 'commit'."
            }
        ), 400

    repository_path = Path(repository)

    if not repository_path.is_absolute():
        repository_path = (
            PROJECT_ROOT / repository_path
        )

    repository_path = repository_path.resolve()

    if not repository_path.exists():
        return jsonify(
            {
                "error": (
                    f"Repository not found: "
                    f"{repository}"
                )
            }
        ), 404

    try:
        result = predict_commit(
            str(repository_path),
            commit,
        )

        return jsonify(result)

    except Exception as exc:
        return jsonify(
            {
                "error": str(exc)
            }
        ), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )