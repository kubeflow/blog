"""Run the lab's mock endpoint as a standalone HTTP service."""

from __future__ import annotations

import argparse

from retry_safe_llm_eval.service import LabHTTPServer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-path", default="/data/state.sqlite3")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=8080, type=int)
    args = parser.parse_args()

    server = LabHTTPServer((args.host, args.port), args.db_path)
    print(f"Mock LLM endpoint listening on {args.host}:{args.port}; SQLite={args.db_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
