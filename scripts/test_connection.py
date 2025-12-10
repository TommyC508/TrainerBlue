#!/usr/bin/env python3
"""
Diagnostic script to test Pokemon Showdown connectivity.
"""
import asyncio
import socket
import websockets
import sys

SERVERS = [
    "sim.smogon.com:8000",
    "sim.psim.us:8000", 
    "sim3.psim.us:8000",
    "sim2.psim.us:8000",
]

def test_tcp_connection(host: str, port: int, timeout: int = 5) -> bool:
    """Test if we can establish a TCP connection."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"  TCP Error: {e}")
        return False

async def test_websocket_connection(server_url: str) -> bool:
    """Test if we can establish a WebSocket connection."""
    try:
        uri = f"ws://{server_url}/showdown/websocket"
        print(f"  Attempting WebSocket connection to {uri}...")
        
        async with websockets.connect(
            uri,
            open_timeout=10,
            ping_timeout=10
        ) as ws:
            print(f"  ✓ WebSocket connected!")
            # Wait for initial message
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"  ✓ Received message: {msg[:100]}...")
            return True
            
    except asyncio.TimeoutError:
        print(f"  ✗ WebSocket timeout")
        return False
    except Exception as e:
        print(f"  ✗ WebSocket error: {type(e).__name__}: {e}")
        return False

async def main():
    print("=" * 60)
    print("Pokemon Showdown Connection Diagnostics")
    print("=" * 60)
    print()
    
    working_servers = []
    
    for server_url in SERVERS:
        print(f"Testing {server_url}:")
        
        # Parse host and port
        host, port = server_url.split(":")
        port = int(port)
        
        # Test TCP connection first
        print(f"  Testing TCP connection to {host}:{port}...")
        tcp_ok = test_tcp_connection(host, port)
        
        if tcp_ok:
            print(f"  ✓ TCP connection successful")
            
            # Test WebSocket connection
            ws_ok = await test_websocket_connection(server_url)
            
            if ws_ok:
                working_servers.append(server_url)
                print(f"  ✓ {server_url} is WORKING!")
        else:
            print(f"  ✗ TCP connection failed")
        
        print()
    
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    
    if working_servers:
        print(f"✓ Found {len(working_servers)} working server(s):")
        for server in working_servers:
            print(f"  - {server}")
        print()
        print(f"Update your .env file with:")
        print(f"PS_SERVER_URL={working_servers[0]}")
    else:
        print("✗ No working servers found.")
        print()
        print("Possible issues:")
        print("  1. Network connectivity issues")
        print("  2. Firewall blocking connections")
        print("  3. Pokemon Showdown servers are down")
        print("  4. Dev container/cloud environment restrictions")
        print()
        print("Solutions:")
        print("  - Check your internet connection")
        print("  - Try running on a different network")
        print("  - Try running locally (not in container)")
        print("  - Check https://pokemonshowdown.com for server status")
        print("  - Try different server URLs from the list above")
    
    print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted by user")
        sys.exit(1)
