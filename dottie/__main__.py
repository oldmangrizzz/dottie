"""Command-line entry point for running Dottie with installed agent handlers.

Agent functions are imported from explicit module:function references.
No eval or arbitrary command execution is used.
"""
import argparse
import importlib
import json
import sys
from .runtime import DottieRuntime

def load_handler(reference):
    module_name, separator, function_name = reference.partition(":")
    if not separator or not module_name or not function_name or not function_name.isidentifier():
        raise ValueError("handler must be module:function")
    module = importlib.import_module(module_name)
    handler = getattr(module, function_name)
    if not callable(handler):
        raise TypeError("agent handler must be callable")
    return handler

def main(argv=None):
    parser = argparse.ArgumentParser(description="Dottie local execution worker")
    parser.add_argument("--database", required=True)
    parser.add_argument("--agent", action="append", default=[], metavar="ID=MODULE:FUNCTION")
    parser.add_argument("--once", action="store_true", help="execute one queued job")
    args = parser.parse_args(argv)
    runtime = DottieRuntime(args.database)
    try:
        for spec in args.agent:
            agent_id, separator, reference = spec.partition("=")
            if not separator or not agent_id:
                parser.error("--agent requires ID=MODULE:FUNCTION")
            runtime.register_agent(agent_id, load_handler(reference))
        if not args.once:
            parser.error("specify --once to execute a queued job")
        result = runtime.run_next()
        print(json.dumps(result))
        return 0 if result is None or result["state"] == "completed" else 1
    finally:
        runtime.close()

if __name__ == "__main__":
    sys.exit(main())
