"""
Performance Optimization Layer
Implements caching, async processing, and performance improvements
"""

import asyncio
import time
import hashlib
import pickle
from functools import wraps
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import os
import json


class CacheManager:
    """Manages caching of OCR results"""
    
    def __init__(self, cache_dir: str = 'temp/cache', max_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_age = timedelta(hours=max_age_hours)
        os.makedirs(cache_dir, exist_ok=True)
        self.memory_cache = {}
        self.max_memory_items = 100
    
    def _get_cache_key(self, filepath: str, options: Dict) -> str:
        """Generate cache key from filepath and options"""
        # Get file modification time
        try:
            mtime = os.path.getmtime(filepath)
        except:
            mtime = 0
        
        # Create key from filepath, mtime, and options
        key_string = f"{filepath}_{mtime}_{json.dumps(options, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, filepath: str, options: Dict) -> Optional[Dict]:
        """Get cached result if available and not expired"""
        cache_key = self._get_cache_key(filepath, options)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            cached_item = self.memory_cache[cache_key]
            if datetime.now() - cached_item['timestamp'] < self.max_age:
                return cached_item['data']
            else:
                del self.memory_cache[cache_key]
        
        # Check disk cache
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_file):
            try:
                # Check file age
                file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                if datetime.now() - file_time < self.max_age:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    
                    # Store in memory cache
                    self._add_to_memory_cache(cache_key, data)
                    return data
                else:
                    # Remove expired cache file
                    os.remove(cache_file)
            except Exception as e:
                print(f"Error reading cache: {e}")
        
        return None
    
    def set(self, filepath: str, options: Dict, data: Dict):
        """Store result in cache"""
        cache_key = self._get_cache_key(filepath, options)
        
        # Store in memory cache
        self._add_to_memory_cache(cache_key, data)
        
        # Store on disk
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Error writing cache: {e}")
    
    def _add_to_memory_cache(self, key: str, data: Dict):
        """Add item to memory cache with LRU eviction"""
        if len(self.memory_cache) >= self.max_memory_items:
            # Remove oldest item
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k]['timestamp']
            )
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def clear(self):
        """Clear all cache"""
        self.memory_cache.clear()
        
        # Clear disk cache
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                except:
                    pass
    
    def clear_expired(self):
        """Remove expired cache entries"""
        # Clear expired memory cache
        expired_keys = [
            key for key, item in self.memory_cache.items()
            if datetime.now() - item['timestamp'] >= self.max_age
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Clear expired disk cache
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if datetime.now() - file_time >= self.max_age:
                        os.remove(filepath)
                except:
                    pass


def cache_result(cache_manager: CacheManager):
    """Decorator to cache function results"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(filepath: str, options: Dict = None, *args, **kwargs):
            if options is None:
                options = {}
            
            # Try to get from cache
            cached = cache_manager.get(filepath, options)
            if cached is not None:
                cached['from_cache'] = True
                return cached
            
            # Execute function
            result = func(filepath, options, *args, **kwargs)
            
            # Store in cache
            if result and 'error' not in result:
                cache_manager.set(filepath, options, result)
                result['from_cache'] = False
            
            return result
        
        return wrapper
    return decorator


class AsyncProcessor:
    """Handles async OCR processing"""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.queue = asyncio.Queue()
    
    async def process_async(self, func: Callable, *args, **kwargs) -> Any:
        """Process function asynchronously with concurrency limit"""
        async with self.semaphore:
            # Run sync function in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)
    
    async def batch_process_async(self, items: list, process_func: Callable) -> list:
        """Process multiple items asynchronously"""
        tasks = [
            self.process_async(process_func, item)
            for item in items
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)


class PerformanceMonitor:
    """Monitors and tracks performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'stage_times': {}
        }
        self.start_time = datetime.now()
    
    def record_request(self, success: bool, processing_time: float, 
                      from_cache: bool = False, stages: Dict = None):
        """Record metrics for a request"""
        self.metrics['total_requests'] += 1
        
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
        
        if from_cache:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
        
        self.metrics['total_processing_time'] += processing_time
        self.metrics['average_processing_time'] = (
            self.metrics['total_processing_time'] / self.metrics['total_requests']
        )
        
        # Record stage times
        if stages:
            for stage, data in stages.items():
                if stage not in self.metrics['stage_times']:
                    self.metrics['stage_times'][stage] = {
                        'total': 0.0,
                        'count': 0,
                        'average': 0.0
                    }
                
                duration = data.get('duration', 0)
                self.metrics['stage_times'][stage]['total'] += duration
                self.metrics['stage_times'][stage]['count'] += 1
                self.metrics['stage_times'][stage]['average'] = (
                    self.metrics['stage_times'][stage]['total'] /
                    self.metrics['stage_times'][stage]['count']
                )
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            **self.metrics,
            'uptime_seconds': uptime,
            'requests_per_minute': (
                self.metrics['total_requests'] / (uptime / 60)
                if uptime > 0 else 0
            ),
            'cache_hit_rate': (
                self.metrics['cache_hits'] / self.metrics['total_requests']
                if self.metrics['total_requests'] > 0 else 0
            ),
            'success_rate': (
                self.metrics['successful_requests'] / self.metrics['total_requests']
                if self.metrics['total_requests'] > 0 else 0
            )
        }
    
    def reset(self):
        """Reset all metrics"""
        self.__init__()


class ImagePreprocessingOptimizer:
    """Optimizes image preprocessing for speed"""
    
    @staticmethod
    def should_preprocess(image_path: str) -> Dict[str, bool]:
        """
        Determine which preprocessing steps are needed
        Returns dict of {step_name: should_apply}
        """
        # This is a simplified version
        # In production, you'd analyze the image to determine needs
        
        return {
            'grayscale': True,
            'denoise': True,
            'enhance_contrast': True,
            'deskew': True,
            'binarize': True
        }
    
    @staticmethod
    def get_optimal_resize_dimensions(width: int, height: int, 
                                     target_dpi: int = 300) -> tuple:
        """Calculate optimal resize dimensions for OCR"""
        # Tesseract works best at ~300 DPI
        # Most documents are 8.5" x 11"
        
        optimal_width = int(8.5 * target_dpi)
        optimal_height = int(11 * target_dpi)
        
        # Calculate aspect ratio
        aspect_ratio = width / height
        
        if aspect_ratio > 1:  # Landscape
            new_width = optimal_width
            new_height = int(new_width / aspect_ratio)
        else:  # Portrait
            new_height = optimal_height
            new_width = int(new_height * aspect_ratio)
        
        return (new_width, new_height)


# Global instances
cache_manager = CacheManager()
performance_monitor = PerformanceMonitor()
async_processor = AsyncProcessor()


def optimize_performance(func: Callable):
    """Decorator to optimize function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = {'error': str(e)}
            success = False
        
        processing_time = time.time() - start_time
        
        # Record metrics
        from_cache = result.get('from_cache', False) if isinstance(result, dict) else False
        stages = result.get('processing', {}).get('stages', {}) if isinstance(result, dict) else {}
        
        performance_monitor.record_request(
            success=success,
            processing_time=processing_time,
            from_cache=from_cache,
            stages=stages
        )
        
        return result
    
    return wrapper


if __name__ == '__main__':
    # Test cache manager
    cache = CacheManager()
    
    # Simulate caching
    test_data = {'result': 'Test OCR result', 'confidence': 0.95}
    cache.set('test.jpg', {'preprocess': True}, test_data)
    
    # Retrieve from cache
    cached = cache.get('test.jpg', {'preprocess': True})
    print("Cached result:", cached)
    
    # Get metrics
    metrics = performance_monitor.get_metrics()
    print("\nPerformance Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
