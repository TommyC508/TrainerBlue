"""Main entry point for Pokemon Showdown agent."""
import asyncio
import argparse
import logging
from pathlib import Path

from .utils import setup_logging, load_env, get_env, load_config
from .connection import ShowdownClient
from .agents import RandomAgent, HeuristicAgent
from .battle_handler import BattleHandler

logger = logging.getLogger(__name__)


async def main():
    """Main function."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Pokemon Showdown AI Agent")
    parser.add_argument("--agent", type=str, default="heuristic", 
                       choices=["random", "heuristic"],
                       help="Agent type to use")
    parser.add_argument("--battles", type=int, default=1,
                       help="Number of battles to play")
    parser.add_argument("--format", type=str, default="gen9randombattle",
                       help="Battle format")
    parser.add_argument("--log-level", type=str, default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    args = parser.parse_args()
    
    # Setup logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    setup_logging(level=args.log_level, log_file="logs/agent.log")
    
    logger.info("=== Pokemon Showdown Agent ===")
    logger.info(f"Agent type: {args.agent}")
    logger.info(f"Format: {args.format}")
    logger.info(f"Battles: {args.battles}")
    
    # Load environment variables
    load_env()
    
    # Get credentials
    username = get_env("PS_USERNAME")
    password = get_env("PS_PASSWORD")
    # Prefer a local Pokémon Showdown server (official engine) when available.
    # Falls back to the public server if PS_SERVER_URL is not set or local isn't reachable.
    configured_server_url = get_env("PS_SERVER_URL")
    server_candidates = [configured_server_url] if configured_server_url else [
        "localhost:8000",
        "sim3.psim.us:8000",
    ]
    
    if not username:
        logger.error("PS_USERNAME not set in .env file")
        return
    
    logger.info(f"Username: {username}")
    
    # Create agent
    if args.agent == "random":
        agent = RandomAgent()
    elif args.agent == "heuristic":
        agent = HeuristicAgent()
    else:
        logger.error(f"Unknown agent type: {args.agent}")
        return
    
    logger.info(f"Created agent: {agent.name}")
    
    client = None
    
    try:
        # Connect and login (try candidates in order)
        last_error: Exception | None = None
        for server_url in server_candidates:
            if not server_url:
                continue
            try:
                logger.info(f"Trying Pokemon Showdown server: {server_url}")
                client = ShowdownClient(server_url, username, password)
                await client.connect()
                await client.login()
                last_error = None
                break
            except Exception as e:
                last_error = e
                try:
                    if client:
                        await client.disconnect()
                except Exception:
                    pass
                client = None

        if not client:
            raise RuntimeError(
                "Could not connect/login to any configured Pokemon Showdown server. "
                "If you want to run locally, start it with scripts/run_showdown_server.sh and set PS_SERVER_URL=localhost:8000."
            ) from last_error
        
        logger.info("Connected and logged in successfully")
        
        # Track battles
        battles_completed = 0
        active_battles = {}
        
        # Battle message handler
        async def handle_battle_message(room_id: str, line: str):
            if room_id not in active_battles:
                # New battle
                handler = BattleHandler(client, agent, room_id)
                active_battles[room_id] = handler
                client.register_battle_handler(room_id, handler.handle_message)
            
            handler = active_battles[room_id]
            await handler.handle_message(room_id, line)
            
            # Check if battle finished
            if handler.finished:
                nonlocal battles_completed
                battles_completed += 1
                del active_battles[room_id]
                client.unregister_battle_handler(room_id)
                
                logger.info(f"Battles completed: {battles_completed}/{args.battles}")
                
                # Search for next battle if needed
                if battles_completed < args.battles:
                    await asyncio.sleep(3)
                    await client.search_battle(args.format)
        
        # Register global battle handler (will create handlers per battle)
        async def global_handler(room_id: str, line: str):
            if room_id.startswith("battle-"):
                await handle_battle_message(room_id, line)
        
        # Start searching for battles
        await client.search_battle(args.format)
        logger.info(f"Searching for {args.format} battle...")
        
        # Listen for messages
        listen_task = asyncio.create_task(client.listen())
        
        # Wait for all battles to complete
        while battles_completed < args.battles:
            await asyncio.sleep(1)
        
        # Cancel search if still active
        if not active_battles:
            await client.cancel_search()
        
        # Wait a bit for cleanup
        await asyncio.sleep(2)
        
        # Print statistics
        logger.info("\n=== Battle Statistics ===")
        logger.info(f"Agent: {agent.name}")
        logger.info(f"Battles played: {agent.battles_played}")
        logger.info(f"Battles won: {agent.battles_won}")
        logger.info(f"Win rate: {agent.win_rate:.1f}%")
        
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        # Disconnect
        if client:
            await client.disconnect()
        logger.info("Disconnected")


if __name__ == "__main__":
    asyncio.run(main())
