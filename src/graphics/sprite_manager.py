"""
Sprite Manager for Pokemon Battle Simulator
Downloads and caches sprites from Pokemon Showdown
"""
import os
import requests
from typing import Dict, Optional
from pathlib import Path
import hashlib

class SpriteManager:
    """Manages Pokemon sprites from Pokemon Showdown"""
    
    # Pokemon Showdown sprite base URLs
    SPRITE_URLS = {
        'front': 'https://play.pokemonshowdown.com/sprites/ani/',
        'back': 'https://play.pokemonshowdown.com/sprites/ani-back/',
        'front_static': 'https://play.pokemonshowdown.com/sprites/gen5/',
        'back_static': 'https://play.pokemonshowdown.com/sprites/gen5-back/',
        'icons': 'https://play.pokemonshowdown.com/sprites/pokemonicons-sheet.png',
    }
    
    def __init__(self, cache_dir: str = ".sprite_cache"):
        """Initialize sprite manager with cache directory"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.loaded_sprites: Dict[str, str] = {}
        
    def _normalize_name(self, species: str) -> str:
        """Normalize Pokemon species name for URL"""
        # Convert to lowercase and handle special cases
        name = species.lower()
        name = name.replace(' ', '')
        name = name.replace("'", '')
        name = name.replace('.', '')
        name = name.replace(':', '')
        
        # Special forme handling
        forme_map = {
            'nidoranf': 'nidoranf',
            'nidoranm': 'nidoranm',
            'farfetchd': 'farfetchd',
            'mr.mime': 'mrmime',
            'mimejr.': 'mimejr',
            'porygon-z': 'porygonz',
            'jangmo-o': 'jangmoo',
            'hakamo-o': 'hakamoo',
            'kommo-o': 'kommoo',
            'type:null': 'typenull',
            'tapu koko': 'tapukoko',
            'tapu lele': 'tapulele',
            'tapu bulu': 'tapubulu',
            'tapu fini': 'tapufini',
        }
        
        return forme_map.get(name, name)
    
    def get_sprite_url(self, species: str, shiny: bool = False, back: bool = False, animated: bool = True) -> str:
        """Get sprite URL for a Pokemon"""
        normalized = self._normalize_name(species)
        
        if animated:
            base_url = self.SPRITE_URLS['back'] if back else self.SPRITE_URLS['front']
            extension = '.gif'
        else:
            base_url = self.SPRITE_URLS['back_static'] if back else self.SPRITE_URLS['front_static']
            extension = '.png'
        
        prefix = 'shiny/' if shiny else ''
        return f"{base_url}{prefix}{normalized}{extension}"
    
    def download_sprite(self, species: str, shiny: bool = False, back: bool = False, animated: bool = True) -> Optional[str]:
        """Download sprite and cache it locally"""
        url = self.get_sprite_url(species, shiny, back, animated)
        
        # Generate cache filename
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        extension = '.gif' if animated else '.png'
        cache_file = self.cache_dir / f"{species.lower().replace(' ', '_')}_{url_hash}{extension}"
        
        # Check cache first
        if cache_file.exists():
            return str(cache_file)
        
        # Download sprite
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded sprite: {species}")
            return str(cache_file)
        except requests.RequestException as e:
            print(f"Failed to download sprite for {species}: {e}")
            return None
    
    def get_sprite(self, species: str, shiny: bool = False, back: bool = False, animated: bool = True) -> Optional[str]:
        """Get cached sprite or download if needed"""
        cache_key = f"{species}_{shiny}_{back}_{animated}"
        
        if cache_key in self.loaded_sprites:
            return self.loaded_sprites[cache_key]
        
        sprite_path = self.download_sprite(species, shiny, back, animated)
        if sprite_path:
            self.loaded_sprites[cache_key] = sprite_path
        
        return sprite_path
    
    def preload_common_pokemon(self, pokemon_list: list[str]):
        """Preload sprites for common Pokemon"""
        print("Preloading sprites...")
        for species in pokemon_list:
            # Preload both front and back
            self.get_sprite(species, back=False, animated=True)
            self.get_sprite(species, back=True, animated=True)
        print(f"Preloaded {len(pokemon_list)} Pokemon sprites")
    
    def clear_cache(self):
        """Clear sprite cache"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir()
        self.loaded_sprites.clear()
        print("Sprite cache cleared")


if __name__ == "__main__":
    # Test sprite manager
    manager = SpriteManager()
    
    # Download some test sprites
    test_pokemon = ['Charizard', 'Blastoise', 'Venusaur', 'Pikachu']
    
    for pokemon in test_pokemon:
        front = manager.get_sprite(pokemon, back=False)
        back = manager.get_sprite(pokemon, back=True)
        print(f"{pokemon}: front={front}, back={back}")
