import logging

import click

from .owl_api import OwlAPI

logger = logging.getLogger("owl-server")


@click.group()
def cli():
    """OWL Server - A simple server for OWL operations."""


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--debug/--no-debug", default=False, help="Enable debug mode")
def start(file_path: str, debug: bool):
    """Start the OWL server with the given ontology file."""
    try:
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")

        api = OwlAPI(file_path)
        logger.info(f"Server started with ontology file: {file_path}")

        # Keep the server running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            api.stop()

    except Exception:
        logger.exception("Server error")
        raise


@cli.command()
@click.argument("file_path", type=click.Path())
def init(file_path: str):
    """Initialize a new OWL file with default prefixes."""
    try:
        api = OwlAPI(file_path)
        api.add_prefix("owl:", "http://www.w3.org/2002/07/owl#")
        api.add_prefix("rdf:", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        api.add_prefix("rdfs:", "http://www.w3.org/2000/01/rdf-schema#")
        api.add_prefix("xsd:", "http://www.w3.org/2001/XMLSchema#")
        logger.info(f"Initialized OWL file: {file_path}")
    except Exception:
        logger.exception("Error initializing OWL file")
        raise


def main():
    """Main entry point for the server."""
    cli()


if __name__ == "__main__":
    main()
