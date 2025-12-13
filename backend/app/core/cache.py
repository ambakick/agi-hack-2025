"""
File-based caching system for YouTube data.
Persists search results and transcripts across server restarts.
"""
import json
import hashlib
import logging
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class FileCache:
    """Thread-safe file-based cache with hash-based keys."""
    
    def __init__(self, cache_dir: str = "cache"):
        # Make cache_dir relative to the app/core directory if not absolute
        if not Path(cache_dir).is_absolute():
            # Get the directory of this file (app/core) and go up 2 levels to backend/
            base_dir = Path(__file__).parent.parent.parent
            self.cache_dir = base_dir / cache_dir
        else:
            self.cache_dir = Path(cache_dir)
        
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Separate directories for different cache types
        self.search_cache_dir = self.cache_dir / "searches"
        self.transcript_cache_dir = self.cache_dir / "transcripts"
        
        self.search_cache_dir.mkdir(exist_ok=True)
        self.transcript_cache_dir.mkdir(exist_ok=True)
        
        # Hashmap files
        self.search_hashmap_file = self.cache_dir / "search_hashmap.json"
        self.transcript_hashmap_file = self.cache_dir / "transcript_hashmap.json"
        
        # In-memory hashmaps for fast lookup
        self.search_hashmap: Dict[str, str] = {}
        self.transcript_hashmap: Dict[str, str] = {}
        
        # Thread locks for thread safety
        self.search_lock = threading.Lock()
        self.transcript_lock = threading.Lock()
        
        # Load existing hashmaps from disk
        self._load_hashmaps()
        
        logger.info(f"Cache initialized at {self.cache_dir.absolute()}")
        logger.info(f"Loaded {len(self.search_hashmap)} search cache entries")
        logger.info(f"Loaded {len(self.transcript_hashmap)} transcript cache entries")
    
    def _load_hashmaps(self):
        """Load hashmaps from disk on startup."""
        try:
            if self.search_hashmap_file.exists():
                with open(self.search_hashmap_file, 'r') as f:
                    self.search_hashmap = json.load(f)
        except Exception as e:
            logger.error(f"Error loading search hashmap: {e}")
            self.search_hashmap = {}
        
        try:
            if self.transcript_hashmap_file.exists():
                with open(self.transcript_hashmap_file, 'r') as f:
                    self.transcript_hashmap = json.load(f)
        except Exception as e:
            logger.error(f"Error loading transcript hashmap: {e}")
            self.transcript_hashmap = {}
    
    def _save_search_hashmap(self):
        """Save search hashmap to disk."""
        try:
            with open(self.search_hashmap_file, 'w') as f:
                json.dump(self.search_hashmap, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving search hashmap: {e}")
    
    def _save_transcript_hashmap(self):
        """Save transcript hashmap to disk."""
        try:
            with open(self.transcript_hashmap_file, 'w') as f:
                json.dump(self.transcript_hashmap, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving transcript hashmap: {e}")
    
    def _hash_key(self, key: str) -> str:
        """Generate a hash for a cache key."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def get_search_results(self, query: str, max_results: int = 10) -> Optional[Any]:
        """
        Get cached search results for a query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results (part of cache key)
        
        Returns:
            Cached search results or None if not found
        """
        cache_key = f"{query}:{max_results}"
        file_hash = self._hash_key(cache_key)
        
        with self.search_lock:
            if cache_key in self.search_hashmap:
                cache_file = self.search_cache_dir / f"{file_hash}.json"
                if cache_file.exists():
                    try:
                        with open(cache_file, 'r') as f:
                            cached_data = json.load(f)
                        logger.info(f"Cache HIT for search: '{query}' (max_results={max_results})")
                        return cached_data['results']
                    except Exception as e:
                        logger.error(f"Error reading search cache: {e}")
                        return None
        
        logger.info(f"Cache MISS for search: '{query}' (max_results={max_results})")
        return None
    
    def set_search_results(self, query: str, results: Any, max_results: int = 10):
        """
        Cache search results for a query.
        
        Args:
            query: Search query string
            results: Search results to cache
            max_results: Maximum number of results (part of cache key)
        """
        cache_key = f"{query}:{max_results}"
        file_hash = self._hash_key(cache_key)
        cache_file = self.search_cache_dir / f"{file_hash}.json"
        
        with self.search_lock:
            try:
                cache_data = {
                    "query": query,
                    "max_results": max_results,
                    "cached_at": datetime.utcnow().isoformat(),
                    "results": results
                }
                
                with open(cache_file, 'w') as f:
                    json.dump(cache_data, f, indent=2)
                
                self.search_hashmap[cache_key] = file_hash
                self._save_search_hashmap()
                
                logger.info(f"Cached search results for: '{query}' (max_results={max_results})")
            except Exception as e:
                logger.error(f"Error caching search results: {e}")
    
    def get_transcript(self, video_id: str) -> Optional[str]:
        """
        Get cached transcript for a video.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Cached transcript text or None if not found
        """
        file_hash = self._hash_key(video_id)
        
        with self.transcript_lock:
            if video_id in self.transcript_hashmap:
                cache_file = self.transcript_cache_dir / f"{file_hash}.json"
                if cache_file.exists():
                    try:
                        with open(cache_file, 'r') as f:
                            cached_data = json.load(f)
                        logger.info(f"Cache HIT for transcript: {video_id}")
                        return cached_data['transcript']
                    except Exception as e:
                        logger.error(f"Error reading transcript cache: {e}")
                        return None
        
        logger.info(f"Cache MISS for transcript: {video_id}")
        return None
    
    def set_transcript(self, video_id: str, transcript: str):
        """
        Cache transcript for a video.
        
        Args:
            video_id: YouTube video ID
            transcript: Transcript text to cache
        """
        file_hash = self._hash_key(video_id)
        cache_file = self.transcript_cache_dir / f"{file_hash}.json"
        
        with self.transcript_lock:
            try:
                cache_data = {
                    "video_id": video_id,
                    "cached_at": datetime.utcnow().isoformat(),
                    "transcript": transcript
                }
                
                with open(cache_file, 'w') as f:
                    json.dump(cache_data, f, indent=2)
                
                self.transcript_hashmap[video_id] = file_hash
                self._save_transcript_hashmap()
                
                logger.info(f"Cached transcript for video: {video_id}")
            except Exception as e:
                logger.error(f"Error caching transcript: {e}")
    
    def clear_search_cache(self):
        """Clear all search cache data."""
        with self.search_lock:
            try:
                for file in self.search_cache_dir.glob("*.json"):
                    file.unlink()
                self.search_hashmap.clear()
                self._save_search_hashmap()
                logger.info("Search cache cleared")
            except Exception as e:
                logger.error(f"Error clearing search cache: {e}")
    
    def clear_transcript_cache(self):
        """Clear all transcript cache data."""
        with self.transcript_lock:
            try:
                for file in self.transcript_cache_dir.glob("*.json"):
                    file.unlink()
                self.transcript_hashmap.clear()
                self._save_transcript_hashmap()
                logger.info("Transcript cache cleared")
            except Exception as e:
                logger.error(f"Error clearing transcript cache: {e}")
    
    def clear_all(self):
        """Clear all cache data."""
        self.clear_search_cache()
        self.clear_transcript_cache()
        logger.info("All cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "search_entries": len(self.search_hashmap),
            "transcript_entries": len(self.transcript_hashmap),
            "cache_dir": str(self.cache_dir.absolute()),
            "search_cache_size_mb": sum(
                f.stat().st_size for f in self.search_cache_dir.glob("*.json")
            ) / (1024 * 1024),
            "transcript_cache_size_mb": sum(
                f.stat().st_size for f in self.transcript_cache_dir.glob("*.json")
            ) / (1024 * 1024)
        }


# Global cache instance
cache = FileCache(cache_dir="cache")

