from django.core.management.base import BaseCommand
from security.camunda_workers import start_security_workers
from wallets.camunda_workers import start_wallet_workers
import logging
import sys
import signal
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Starts all Camunda external task workers'

    def __init__(self):
        super().__init__()
        self.workers = []
        self.running = True

    def handle(self, *args, **options):
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

        try:
            self.stdout.write(self.style.SUCCESS('Starting Camunda workers...'))
            
            # Start security workers
            security_client = start_security_workers()
            self.workers.append(security_client)
            self.stdout.write(self.style.SUCCESS('Security workers started'))
            
            # Start wallet workers
            wallet_client = start_wallet_workers()
            self.workers.append(wallet_client)
            self.stdout.write(self.style.SUCCESS('Wallet workers started'))
            
            # Keep the command running
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error starting workers: {str(e)}'))
            logger.error('Failed to start Camunda workers', exc_info=True)
            sys.exit(1)

    def handle_shutdown(self, signum, frame):
        """Handle graceful shutdown of workers"""
        self.stdout.write(self.style.WARNING('\nShutting down workers...'))
        self.running = False
        
        for worker in self.workers:
            try:
                worker.stop()
            except Exception as e:
                logger.error(f'Error stopping worker: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS('Workers stopped successfully'))
        sys.exit(0)