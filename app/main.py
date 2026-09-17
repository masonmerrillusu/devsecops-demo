"""Container Security Self-Check: a tiny site that reports on its own runtime security."""
import os
import platform
import socket

from flask import Flask, jsonify, render_template

app = Flask(__name__)


def get_user():
    """Return (username, uid) for the user this process is running as."""
    try:
        import pwd  # Unix-only module, so import it inside the try

        uid = os.getuid()
        return pwd.getpwuid(uid).pw_name, uid
    except (ImportError, AttributeError, KeyError):
        # Windows has no pwd module or os.getuid(); KeyError covers a UID
        # with no /etc/passwd entry (e.g. docker run -u 12345).
        return os.environ.get("USERNAME", "unknown"), -1


def build_checks(username, uid, port):
    """Pure function: takes facts in, returns pass/fail results out.

    It never reads the real environment itself, which is what lets the
    unit tests simulate root or a privileged port without being root.
    """
    return [
        {
            "name": "Running as non-root user",
            "value": f"{username} (uid {uid})",
            "passed": uid != 0,
        },
        {
            "name": "Listening on unprivileged port (>= 1024)",
            "value": str(port),
            "passed": port >= 1024,
        },
    ]


@app.route("/")
def index():
    username, uid = get_user()
    port = int(os.environ.get("PORT", "8000"))
    info = {
        "Container ID": socket.gethostname(),
        "Python version": platform.python_version(),
        "Git commit": os.environ.get("GIT_SHA", "unknown")[:7],
        "Build time": os.environ.get("BUILD_TIME", "unknown"),
    }
    return render_template(
        "index.html", checks=build_checks(username, uid, port), info=info
    )


@app.route("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)