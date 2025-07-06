"""
Command-line interface for Gmail Email Agent
"""

import asyncio
import click
import sys
import os
from datetime import datetime
from typing import List

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_agent import EmailAgent
from models import EmailSummary
from utils import format_email_summary


@click.group()
@click.option('--config', default='config/config.yaml', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Gmail Email Agent - Intelligent email management system"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config


@cli.command()
@click.pass_context
def listen(ctx):
    """Start the email listener mode"""
    click.echo("Starting Gmail Email Agent in listener mode...")
    
    async def run_listener():
        agent = EmailAgent(ctx.obj['config'])
        try:
            await agent.initialize()
            click.echo("✓ Agent initialized successfully")
            click.echo("✓ Listening for new emails... (Press Ctrl+C to stop)")
            await agent.start_listener_mode()
        except KeyboardInterrupt:
            click.echo("\n⚠ Received interrupt signal")
        except Exception as e:
            click.echo(f"✗ Error: {e}", err=True)
            sys.exit(1)
        finally:
            await agent.stop()
            click.echo("✓ Agent stopped")
    
    asyncio.run(run_listener())


@cli.command()
@click.option('--timeframe', default='7d', help='Timeframe to process (e.g., 7d, 2w, 1m)')
@click.pass_context
def batch(ctx, timeframe):
    """Process past emails in batch mode"""
    click.echo(f"Starting batch processing for timeframe: {timeframe}")
    
    async def run_batch():
        agent = EmailAgent(ctx.obj['config'])
        try:
            await agent.initialize()
            click.echo("✓ Agent initialized successfully")
            
            with click.progressbar(length=1, label='Processing emails') as bar:
                await agent.run_batch_processor(timeframe)
                bar.update(1)
            
            # Show statistics
            stats = await agent.get_processing_stats()
            click.echo("\n📊 Processing Statistics:")
            click.echo(f"  Total Processed: {stats['total_processed']}")
            click.echo(f"  Important: {stats['important_count']}")
            click.echo(f"  Promotional: {stats['promotional_count']}")
            click.echo(f"  Social: {stats['social_count']}")
            click.echo(f"  Junk: {stats['junk_count']}")
            
        except Exception as e:
            click.echo(f"✗ Error: {e}", err=True)
            sys.exit(1)
        finally:
            await agent.stop()
    
    asyncio.run(run_batch())


@cli.command()
@click.pass_context
def junk(ctx):
    """Detect and review potential junk emails"""
    click.echo("Starting junk detection...")
    
    async def run_junk_detection():
        agent = EmailAgent(ctx.obj['config'])
        try:
            await agent.initialize()
            click.echo("✓ Agent initialized successfully")
            
            # Get junk email summaries
            summaries = await agent.run_junk_detector()
            
            if not summaries:
                click.echo("✓ No junk emails found!")
                return
            
            click.echo(f"\n🗑 Found {len(summaries)} potential junk emails:")
            click.echo("=" * 80)
            
            # Display summaries
            for i, summary in enumerate(summaries, 1):
                click.echo(f"\n{i}. {summary.sender}")
                click.echo(f"   Subject: {summary.subject}")
                click.echo(f"   Date: {summary.date.strftime('%Y-%m-%d %H:%M')}")
                click.echo(f"   Confidence: {summary.confidence:.2f}")
                click.echo(f"   Preview: {summary.snippet[:100]}...")
            
            click.echo("=" * 80)
            
            # Ask for confirmation
            if click.confirm(f"\nDelete all {len(summaries)} junk emails?"):
                email_ids = [s.email_id for s in summaries]
                await agent.delete_confirmed_junk(email_ids)
                click.echo(f"✓ Deleted {len(email_ids)} junk emails")
            else:
                click.echo("⚠ No emails deleted")
            
        except Exception as e:
            click.echo(f"✗ Error: {e}", err=True)
            sys.exit(1)
        finally:
            await agent.stop()
    
    asyncio.run(run_junk_detection())


@cli.command()
@click.pass_context
def stats(ctx):
    """Show processing statistics"""
    
    async def show_stats():
        agent = EmailAgent(ctx.obj['config'])
        try:
            await agent.initialize()
            
            # Get current stats
            stats = await agent.get_processing_stats()
            
            click.echo("📊 Gmail Email Agent Statistics")
            click.echo("=" * 40)
            click.echo(f"Status: {'Running' if stats['running'] else 'Stopped'}")
            click.echo(f"Last Check: {stats['last_check'] or 'Never'}")
            click.echo(f"Total Processed: {stats['total_processed']}")
            click.echo(f"Important Emails: {stats['important_count']}")
            click.echo(f"Promotional Emails: {stats['promotional_count']}")
            click.echo(f"Social Emails: {stats['social_count']}")
            click.echo(f"Junk Emails: {stats['junk_count']}")
            click.echo(f"Errors: {stats['errors']}")
            
            # Get database info
            db_info = await agent.database_manager.get_database_info()
            if db_info:
                click.echo("\n💾 Database Information")
                click.echo("=" * 30)
                click.echo(f"Path: {db_info.get('database_path', 'Unknown')}")
                
                from utils import format_file_size
                size = db_info.get('file_size_bytes', 0)
                click.echo(f"Size: {format_file_size(size)}")
                
                table_counts = db_info.get('table_counts', {})
                for table, count in table_counts.items():
                    click.echo(f"{table.replace('_', ' ').title()}: {count}")
            
        except Exception as e:
            click.echo(f"✗ Error: {e}", err=True)
            sys.exit(1)
        finally:
            await agent.stop()
    
    asyncio.run(show_stats())


@cli.command()
@click.option('--days', default=90, help='Clean data older than N days')
@click.pass_context
def cleanup(ctx, days):
    """Clean up old data from database"""
    click.echo(f"Cleaning up data older than {days} days...")
    
    if not click.confirm("This will permanently delete old data. Continue?"):
        click.echo("Cleanup cancelled")
        return
    
    async def run_cleanup():
        agent = EmailAgent(ctx.obj['config'])
        try:
            await agent.initialize()
            await agent.database_manager.cleanup_old_data(days)
            click.echo(f"✓ Cleaned up data older than {days} days")
            
        except Exception as e:
            click.echo(f"✗ Error: {e}", err=True)
            sys.exit(1)
        finally:
            await agent.stop()
    
    asyncio.run(run_cleanup())


@cli.command()
@click.option('--backup-path', help='Path for backup file')
@click.pass_context
def backup(ctx, backup_path):
    """Create database backup"""
    
    if not backup_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"data/backup_email_agent_{timestamp}.db"
    
    click.echo(f"Creating backup: {backup_path}")
    
    async def run_backup():
        agent = EmailAgent(ctx.obj['config'])
        try:
            await agent.initialize()
            await agent.database_manager.backup_database(backup_path)
            click.echo(f"✓ Backup created: {backup_path}")
            
        except Exception as e:
            click.echo(f"✗ Error: {e}", err=True)
            sys.exit(1)
        finally:
            await agent.stop()
    
    asyncio.run(run_backup())


@cli.command()
@click.pass_context
def test(ctx):
    """Test Gmail API connection and basic functionality"""
    click.echo("Testing Gmail Email Agent...")
    
    async def run_test():
        agent = EmailAgent(ctx.obj['config'])
        try:
            click.echo("1. Initializing agent...")
            await agent.initialize()
            click.echo("   ✓ Agent initialized")
            
            click.echo("2. Testing Gmail connection...")
            # This is tested during initialization
            click.echo("   ✓ Gmail connection successful")
            
            click.echo("3. Testing AI classifier...")
            test_email = {
                'id': 'test_123',
                'sender': 'test@example.com',
                'subject': 'Test Email',
                'body': 'This is a test email.',
                'date': datetime.now()
            }
            classification = await agent.ai_classifier.classify_email(test_email)
            click.echo(f"   ✓ AI classification: {classification.category.value} (confidence: {classification.confidence:.2f})")
            
            click.echo("4. Testing database...")
            await agent.database_manager.save_classification(classification)
            click.echo("   ✓ Database operations successful")
            
            click.echo("\n🎉 All tests passed! Email Agent is ready to use.")
            
        except Exception as e:
            click.echo(f"✗ Test failed: {e}", err=True)
            sys.exit(1)
        finally:
            await agent.stop()
    
    asyncio.run(run_test())


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information"""
    click.echo("Gmail Email Agent v1.0.0")
    click.echo("Intelligent email management system")
    click.echo("Built with Python, Gmail API, and OpenAI")


if __name__ == '__main__':
    cli()
