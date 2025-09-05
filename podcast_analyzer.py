#!/usr/bin/env python3
"""
Podcast Analyzer - Download, transcribe, and summarize podcasts
"""

import click
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import the new Celery task
from tasks import analyze_episode

# Load environment variables from .env file
load_dotenv()

@click.group()
def cli():
    """Podcast Analyzer CLI"""
    pass

@cli.command()
@click.argument('url')
@click.option('--force', is_flag=True, help='Reprocess episode even if already analyzed')
def analyze(url, force):
    """
    Queue a podcast episode for analysis.
    """
    try:
        # Instead of calling the function directly, we call '.delay()' to send it to the Celery queue
        click.echo(f"Queuing episode for analysis: {url}")
        analyze_episode.delay(url, force)
        click.echo("Episode successfully queued.")
    except Exception as e:
        click.echo(f"An unexpected error occurred while queuing: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli()